"""Facebook module."""
from __future__ import absolute_import

from collections import OrderedDict
import contextlib
import itertools
import datetime
import urllib
import urlparse
import json

import facebook
import pytz

from wrap2.core import SocialNetwork


class Facebook(SocialNetwork):
    """Facebook social network wrapper."""

    # Use a mobile version by default as the package is used in mobile app, (can be overridden to normal if any need).
    FB_OATH_BASE = 'http://m.facebook.com/dialog/oauth?'
    FB_OATH_ACCT = 'https://graph.facebook.com/oauth/access_token?'
    FB_PROFILE_BASE = 'https://graph.facebook.com/me?'

    def get_authorization_url(self, callback_url, scope=()):
        """
        See :meth:`SocialNetwork.get_auhtorization_url()` for the basics on this
        method.

        Returns a tuple of length 1 containing the URL where the user can
        authorize (login) into Facebook and give your application permission to
        read data from his profile.

        The scope is a list of permissions (as string values) for the resulting
        ``access_token`` from :met:`on_authorization_callback()` see:
        https://developers.facebook.com/docs/reference/api/permissions/ for a
        list of possible values.
        """
        args = dict(client_id=self.id, redirect_uri=callback_url, scope=','.join(scope))
        result = self.FB_OATH_BASE + urllib.urlencode(args)
        return (result, ())

    def on_authorization_callback(self, callback_url, code=None):
        """
        See :meth:`SocialNetwork.on_authorization_callback()` for the basics on
        this method.

        The ``code`` is attached to the ``callback_url`` redirect by
        Facebook after the user has logged in at the URL retrieved from
        :meth:`get_authorization_url()`

        :return: a tuple containing:
        (<user-id>, <access-token>, <user-name>, <profile-link>)
        """
        args = dict(client_id=self.id, redirect_uri=callback_url)
        args['code'] = code
        args['client_secret'] = self.secret

        with contextlib.closing(urllib.urlopen(self.FB_OATH_ACCT + urllib.urlencode(args))) as reader:
            body = reader.read()
        response = urlparse.parse_qs(body)

        access_token = response["access_token"][-1]

        # Download the user profile
        with contextlib.closing(
                urllib.urlopen(self.FB_PROFILE_BASE + urllib.urlencode(dict(access_token=access_token)))) as reader:
            profile = json.load(reader)

        return (profile['id'], access_token, profile['name'], profile['link'])

    def post(self, access_token, msg):
        """
        Puts a post on the wall of the user authorized by ``access_token``.

        ``access_token`` can be retrieved via
        :meth:`on_authorization_callback()`

        Returns a dictionary containing {'id':'<id-of-post>'}
        """
        graph = facebook.GraphAPI(access_token)
        post = graph.put_wall_post(msg)

        return post

    def get(self, query, access_token, friends_only=False, count=100):
        """
        Return list of objects which correspond to the ``query``

        :param query: `dict` representing a query params
        :param access_token: required, to access the stream
        :param friends_only: flag to only output the friends related content
        :param count: limit output items count
        """
        graph = facebook.GraphAPI(access_token)

        if friends_only:
            raise NotImplementedError('Search among friends is not implemented.')

        query = dict(OrderedDict(
            posts='SELECT post_id,'
            'actor_id, attachment, comments.count, created_time, likes, message, message_tags, '
            'parent_post_id, permalink, place, post_id, privacy, share_count, source_id, type, '
            'updated_time, target_id '
            'FROM stream WHERE source_id in ({0}) ORDER BY created_time desc LIMIT {1}'
            .format(', '.join(map(str, query['ids'])), count),
            post_actor_info='SELECT uid, name FROM user '
            'WHERE uid IN (SELECT actor_id, target_id FROM #posts)',
            comments='SELECT id, likes, text, text_tags, time, post_id, fromid '
            'FROM comment WHERE post_id in '
            '(SELECT post_id FROM #posts) ORDER BY time desc LIMIT {0}'.format(count),
            comment_actor_info='SELECT uid, name FROM user '
            'WHERE uid IN (SELECT fromid FROM #comments)'))

        result = graph.request('fql', args=dict(q=query))

        #expand results json to make processing easier
        result = dict(((record['name'], record['fql_result_set']) for record in result['data']))

        posts = self.merge_results(result)

        posts.sort(key=lambda x: x['created_at'])

        return posts

    def merge_results(self, result):
        """Merge result into list of posts.
        param result: raw response data from a FQL call to facebook API, which gets posts, comments, profile info.
        return: list of twitter-like dictionary `posts`.
        """

        posts = []
        posts_by_id = {}

        post_data = itertools.izip_longest(
            result['posts'], result['post_actor_info'], fillvalue={'name': '', 'uid': ''}
        )

        for post, actor_info in post_data:
            posts.append(self.post_to_dict(post, actor_info))
            posts_by_id[post['post_id']] = post

        comment_data = itertools.izip_longest(
            result['comments'], result['comment_actor_info'], fillvalue={'name': '', 'uid': ''}
        )

        for comment, actor_info in comment_data:
            posts.append(self.comment_to_dict(comment, actor_info, posts_by_id[comment['post_id']]))
        return posts

    def post_to_dict(self, post, actor_info):
        """
        Convert post to python dict.
        Output should be in exactly same format as twitter or other network supported by
        this package. But we take twitter as standard.

        :param post: post object directly from FB communication
        :param actor_info: actor_info object directly from FB communication. Actor info is an object describing
                           author of the post.
        :return: `dict` in form: {'created_at': datetime.datetime(2012, 1, 1) ...} full format see on the
                 https://dev.twitter.com/docs/api/1.1/get/search/tweets
        """

        return {"text": post["message"],
                "created_at": datetime.datetime.fromtimestamp(post['created_time'], pytz.UTC),
                "entities": {
                    "urls": [
                        {
                            "url": post['permalink'],
                            "expanded_url": post['permalink'],
                            "display_url": post['permalink'],
                            "indices": []  # we don't actually seach, so can't have any indices
                        }
                    ]
                },
                "from_user": actor_info['name'],
                "from_user_id": actor_info['uid'],
                "from_user_id_str": str(actor_info['uid']),
                "geo": None,  # TODO: implement geo tags conversion from FB to TWITTER
                "id": post['post_id'],
                "id_str": str(post['post_id']),
                "iso_language_code": "en",
                "metadata": {
                    "recent_retweets": 0,  # TODO: retweets are irrelevant for FB, but we have reshare count from FB
                    "result_type": "recent"
                }
                }

    def comment_to_dict(self, comment, actor_info, post):
        """
        Convert comment to python dict.
        We consider comments as actually posts. Output should be in exactly same format
        as twitter or other network supported by this package. But we take twitter as standard.

        :param comment: comment object directly from FB communication
        :param actor_info: actor_info object directly from FB communication
        :param post: post_object directly from FB communication. Actor info is an object describing author of the post.
        :return: `dict` in form: {'created_at': datetime.datetime(2012, 1, 1) ...} full format see on the
                 https://dev.twitter.com/docs/api/1.1/get/search/tweets
        """

        # we convert comment to be like post
        comment['permalink'] = '{0}?comment_id={1}'.format(post['permalink'], comment['id'])
        comment['post_id'] = comment['id']
        comment['created_time'] = comment['time']
        comment['message'] = comment['text']

        return self.post_to_dict(comment, actor_info)
