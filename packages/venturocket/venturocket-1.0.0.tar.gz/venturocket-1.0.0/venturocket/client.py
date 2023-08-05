from venturocket.keyword import KeywordClient
from venturocket.listing import ListingClient

__author__ = 'Joe Linn'


class Venturocket(object):
    def __init__(self, key, secret):
        super(Venturocket, self).__init__()
        self._clients = {}
        self._key = key
        self._secret = secret

    def _get_client(self, clazz):
        """

        :param clazz:
        :type clazz: type extends AbstractClient
        :return:
        :rtype: AbstractClient
        """
        if not clazz.__name__ in self._clients:
            self._clients[clazz.__name__] = clazz(self._key, self._secret)
        return self._clients[clazz.__name__]

    @property
    def keyword(self):
        """

        :return:
        :rtype: KeywordClient
        """
        return self._get_client(KeywordClient)

    @property
    def listing(self):
        """

        :return:
        :rtype: ListingClient
        """
        return self._get_client(ListingClient)