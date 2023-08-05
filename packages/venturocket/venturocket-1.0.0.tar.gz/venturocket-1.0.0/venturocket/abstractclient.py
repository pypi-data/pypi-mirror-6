import json

__author__ = 'Joe Linn'

import abc
import requests


class AbstractClient(object):
    __metaclass__ = abc.ABCMeta

    BASE_URL = "https://api.venturocket.com/v1/"

    def __init__(self, api_key, api_secret):
        """
        :param api_key: your Venturocket api key
        :type api_key: str
        :param api_secret: your Venturocket api secret
        :type api_secret: str
        """
        super(AbstractClient, self).__init__()
        self._key = api_key
        self._secret = api_secret

    def _get(self, url, query_params=None):
        """
        Perform a http GET request
        :param url: the url of the desired endpoint
        :type url: str
        :param query_params: optional querystring parameters
        :type query_params: dict
        :return:
        :rtype: dict
        """
        return self._request("GET", url, query_params)

    def _post(self, url, query_params=None, data=None):
        """

        :param url:
        :type url: str
        :param query_params:
        :type query_params: dict
        :param data:
        :type data: dict
        :return:
        :rtype: dict
        """
        return self._request("POST", url, query_params, data)

    def _put(self, url, query_params=None, data=None):
        """

        :param url:
        :type url: str
        :param query_params:
        :type query_params: dict
        :param data:
        :type data: dict
        :return:
        :rtype: dict
        """
        return self._request("PUT", url, query_params, data)

    def _request(self, method, url, query_params=None, data=None):
        """
        Send a request to the API
        :param method: http request method
        :type method: str
        :param url: the url of the desired endpoint
        :type url: str
        :param query_params: optional querystring parameters
        :type query_params: dict
        :param data: optional request body data
        :type data: dict
        :return: the result of the request
        :rtype: dict
        """
        headers = {
            'accept': 'application/json',
            'content-type': 'application/json'
        }
        if data is not None:
            data = json.dumps(data)
        response = requests.request(method, self.BASE_URL + url, params=query_params, data=data,
                                    auth=(self._key + '', self._secret), headers=headers)
        if response.status_code >= 400:
            raise ApiError(response.status_code, response.json()['error'])
        return response.json()


class ApiError(Exception):
    def __init__(self, status, error, *args, **kwargs):
        error_string = "%s - %s" %(status, error)
        super(ApiError, self).__init__(error_string, *args, **kwargs)