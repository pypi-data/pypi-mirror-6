# coding: utf-8
from __future__ import absolute_import
from webob import dec
from .interfaces import _Application

_MIDDILEWARES = []


def register_middleware(middleware):
    # if isinstance(middleware, Middleware):
    #     _MIDDILEWARES.append(middleware)
    _MIDDILEWARES.append(middleware)


def get_middlewares():
    return _MIDDILEWARES


class Middleware(_Application):
    """Base WSGI middleware.

    These classes require an application to be initialized that will be called
    next.  By default the middleware will simply call its wrapped app, or you
    can override __call__ to customize its behavior.

    """

    @classmethod
    def create(cls, *args, **kwargs):
        return cls(*args, **kwargs)

    def __init__(self, application):
        self.application = application

    def process_request(self, req):
        """Called on each request.

        If this returns None, the next application down the stack will be
        executed. If it returns a response then that response will be returned
        and execution will stop here.

        """
        return None

    def process_response(self, response):
        """Do whatever you'd like to the response."""
        return response

    @dec.wsgify()
    def __call__(self, req):
        response = self.process_request(req)
        if response:
            return response
        response = req.get_response(self.application)
        return self.process_response(response)
