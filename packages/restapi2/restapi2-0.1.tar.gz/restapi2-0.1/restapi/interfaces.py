# coding: utf-8
from __future__ import absolute_import
from .responses import Response404


class _Application(object):
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def __call__(self, *args, **kwargs):
        pass


class Controller(object):
    def default(self, *args, **kwargs):
        return Response404()


class Serializer(_Application):
    """Don't serializer at all."""

    def serializer(self, response):
        """Convert the python object, such as a dict or a Response object,
        to the HTTP or HTTPS.

        Args:
            @response: a python built-in type, or a Response object.

        Return: A str, a list of str, or a Response object. The return value
                will be send to the client as the response content.
        """
        return response

    def deserializer(self, request, result=None):
        """Convert the HTTP or HTTPS to a dict object.

        Args:
            @request: a Request object.
            @result: None, or a dict.

        Return: A dict, and it is recieved by the action of the controller with
                the keyword arguments. And you capture it with **kwargs in that
                actoin.
        """
        return result
