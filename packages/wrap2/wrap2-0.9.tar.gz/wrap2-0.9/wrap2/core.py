"""Base abstraction layer for social networks."""
import abc


class SocialNetwork(object):
    """Social Network wrapper base class."""

    def __init__(self, id, secret):
        """
        :param id: network id
        :param secret: network secret
        """
        self.id = id
        self.secret = secret

    @abc.abstractmethod
    def get_authorization_url(self, callback_url, **kwargs):
        """
        Returns a tuple containing the URL for a client to authorize
        with the network. After authorization, the
        network will redirect the client to ``callback_url``.
        The first element of the tuple will always contain the URL,
        second is a tuple which contain network specific results which
        must be used when processing the ``callback_url`` redirect.
        Method receives optional keyword arguments which are network-specific.

        :param callback_url: callback URL after successful authorization

        Use :meth:`on_authorization_callback` to process
        the result from the network redirect.
        """

    @abc.abstractmethod
    def on_authorization_callback(self,
                                  callback_url,
                                  **callback_arguments):
        """
        When a client is authorized and redirected to ``callback_url``
        by the network, this method can process the supplied
        arguments from the network. See :meth:`get_authorization_url`
        for more information.

        :param callback_url: callback URL after successful authorization

        :return: a tuple containing:
        (<user-id>, <access-token>, <user-name>, <profile-link>)
        """

    @abc.abstractmethod
    def post(self, access_token, msg):
        """
        Create a new post and return it.

        :param access_token: authorization token
        :param msg: post message.

        :return: dictionary containing post data (format of twitter is chosen as standard for all networks)
        """

    @abc.abstractmethod
    def get(self, access_token, query):
        """
        Return posts that satisfy the query.

        :param access_token: authorization token
        :param query: search query.

        :return: list of dictionaries containing posts data (format of twitter is chosen as standard for all networks)
        """

    def _to_dict(self, value):
        """
        Helper method to convert complex python objects to plain dictionaries.
        """
        result = {}
        for k, v in value.__dict__.iteritems():
            if not k.startswith('_'):
                result[k] = v
        return result
