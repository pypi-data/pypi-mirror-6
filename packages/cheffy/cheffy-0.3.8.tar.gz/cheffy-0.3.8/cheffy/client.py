# -*- coding: utf-8 -*-
"""
A simple client-wrapper around chef server.
Do low-level http requests to the chef and sign the requests.

"""
import datetime
import socket

import requests
from requests.exceptions import TooManyRedirects, URLRequired,\
    HTTPError, ConnectionError, Timeout

from .auth import sign_request
from . import __version__


class Client:

    def __init__(
        self, key, chef_host, chef_user, headers={},
        schema='http://', content_type="application/json"
    ):
        # private key
        self.key = key
        self.chef_host = chef_host
        self.chef_user = chef_user
        self.schema = schema
        self.request_dict = None
        self.response = None

        self.headers = {
            "content-type": content_type,
            "x-chef-version": "11.4.4",
            "user-agent": "python-cheffy/%s" % __version__
        }

        self.headers.update(headers)

    def release_connection(self):
        """
        Need to close sockets manually. See
        <https://github.com/kennethreitz/requests/issues/239> for the details.
        """
        if self.response:
            self.response.raw.release_conn()
            if self.response.raw._fp.fp is not None:
                sock = self.response.raw._fp.fp._sock
                try:
                    sock.shutdown(socket.SHUT_RDWR)
                    sock.close()
                except socket.error:
                    pass

    def get(self, path, **kwargs):
        return self.__request('GET', path, **kwargs)

    def post(self, path, **kwargs):
        return self.__request('POST', path, **kwargs)

    def delete(self, path, **kwargs):
        return self.__request('DELETE', path, **kwargs)

    def put(self, path, **kwargs):
        return self.__request('PUT', path, **kwargs)

    def __request(self, method, path, data=None, **kwargs):
        auth_headers = sign_request(
            self.key, method, path.split('?', 1)[0], data,
            datetime.datetime.utcnow(), self.chef_user
        )

        req_headers = {}
        req_headers.update(self.headers)
        req_headers.update(
            dict((k.lower(), v) for k, v in self.headers.iteritems())
        )
        req_headers.update(auth_headers)

        req_method = method.lower()

        abs_url = "%s%s%s" % (self.schema, self.chef_host, path)

        # This data returns as first item in response tuple
        # it's useful for debug or logging
        self.request_dict = {
            'url': abs_url,
            'method': req_method,
            'headers': req_headers,
            'data': data,
            'path': path
        }

        # Do request
        try:
            # call the selected method from the requests module
            # it will returns a tuple (request_dict, Response object)
            # or raise an exception
            self.response = getattr(
                requests,  req_method
            )(abs_url, headers=req_headers, data=data)

            return (self.request_dict, self.response)

        # All possibled 'requests' exceptions
        except (
            TooManyRedirects,
            URLRequired,
            HTTPError,
            ConnectionError,
            Timeout
        ) as e:
            raise e

