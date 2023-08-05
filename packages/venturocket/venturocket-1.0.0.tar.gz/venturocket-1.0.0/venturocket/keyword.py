__author__ = 'Joe Linn'

from venturocket.abstractclient import AbstractClient


class KeywordClient(AbstractClient):
    """
    `http://venturocket.com/api/v1#keywords<http://venturocket.com/api/v1#keywords>`_.
    """

    def get_keyword(self, word):
        """
        Retrieve validity and synonym information regarding the requested keyword
        :param word: the desired keyword
        :type word: str
        :return: keyword data
        :rtype: dict
        """
        return self._get("keyword/%s" % word)

    def get_suggestions(self, *words):
        """
        Given one or more keywords, retrieve a list of keywords ordered by descending popularity which are commonly
        used with the given keyword(s)
        :param words: one or more keywords for which to retrieve suggestions
        :type words: str
        :return: a list of suggested keywords
        :rtype: list of str
        """
        return self._get("keyword-suggestions/%s" % ','.join(words))['suggestions']

    def parse_keywords(self, text):
        """
        Parse valid Venturocket keywords from raw text
        :param text: raw text from which to parse keywords
        :type text: str
        :return: a list of valid keywords ordered by descending popularity
        :rtype: list of str
        """
        return self._post("keyword-parser", data={"text": text})['keywords']