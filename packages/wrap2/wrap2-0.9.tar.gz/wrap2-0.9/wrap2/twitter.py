"""Twitter module."""
import tweepy

from wrap2.core import SocialNetwork


class Twitter(SocialNetwork):
    """Twitter social network wrapper."""

    def get_authorization_url(self, callback_url):
        """
        See :meth:`SocialNetwork.get_auhtorization_url()` for the basics on this
        method.

        Returns a tuple containing:
        ``(<URL>, (<request-token-key>, <request-token-secret>))``.
        The ``request-token-*`` pair is used when processing the ``callback_url``
        redirect. See :meth:`on_authorization_callback` for more info.
        """
        auth = tweepy.OAuthHandler(str(self.id), str(self.secret), str(callback_url))
        url = auth.get_authorization_url(signin_with_twitter=True)
        return (url, (auth.request_token.key, auth.request_token.secret))

    def on_authorization_callback(self, callback_url,
                                  oauth_verifier=None,
                                  request_token=None):
        """
        See :meth:`SocialNetwork.on_authorization_callback()` for the basics on
        this method.

        The ``oath_verifier`` is attached to the ``callback_url`` redirect by
        Twitter. The request token must be a tuple containing the
        ``request-token-*`` pair retrieved earlier from
        :meth:`get_authorization_url()`
        """
        auth = tweepy.OAuthHandler(str(self.id), str(self.secret), str(callback_url))
        auth.set_request_token(request_token[0], request_token[1])
        access_token = auth.get_access_token(oauth_verifier)
        auth.set_access_token(access_token.key, access_token.secret)

        api = tweepy.API(auth)

        user = api.me()

        profile_link = 'http://twitter.com/' + user.screen_name

        return (user.id, (access_token.key, access_token.secret), user.name, profile_link)

    def _to_dict(self, value):
        result = super(Twitter, self)._to_dict(value)
        for k, v in result.iteritems():
            if isinstance(v, tweepy.models.Model):
                result[k] = self._to_dict(v)
        return result

    def api(self, access_token=None):
        """If no access token is received some action could be performed anyway.
        So, is allowed to create an API without access_token
        """
        auth = None
        if access_token:
            auth = tweepy.OAuthHandler(str(self.id), str(self.secret))
            auth.set_access_token(access_token[0], access_token[1])
        return tweepy.API(auth)

    def status_to_dict(self, value):
        """Convert status to dict."""
        value.from_user = value.user.screen_name
        value.from_user_name = value.user.name
        value.from_user_id = value.user.id
        value.from_user_id_str = value.user.id_str
        value.profile_image_url = value.user.profile_image_url
        return self._to_dict(value)

    def post(self, access_token, msg):
        """
        Updates the status of the user authorized by ``access_token``.

        ``access_token`` must be a tuple containing ``(<access-token-key>,
        <access-token-secret>)`` and can be retrieved via
        :meth:`on_authorization_callback()`

        Returns the result from
        https://dev.twitter.com/docs/api/1/post/statuses/update
        formatted as a dict. (It seems tweepy renames the tweet's ``user``
        property to ``author`` though)
        """
        post = self.api(access_token).update_status(msg)

        return self._to_dict(post)

    def get(self, query, access_token=None, friends_only=False, count=100):
        """
        Yield statuses which correspond to the ``query``.
        """
        api = self.api(access_token)

        if friends_only:
            user_id = api.me().id
            q = query.lower()

            result = (s for s in api.home_timeline(count=count) if q in s.text.lower() and user_id != s.user.id)
        else:
            result = api.search(query, rpp=100)

        for status in result:
            #status is a tweepy.models.SearchResult
            #instance. wrap2 should return the status representation
            #which is independent on Facebook and Tweeter.
            yield self._to_dict(status)
