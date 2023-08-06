# coding: utf-8
from __future__ import absolute_import
import webob
from webob import dec
from routes import middleware, Mapper as _Mapper
from .utils import strings
from .responses import Response
from .requests import Request
from .serializers import NoSerializer
from .middlewares import get_middlewares
_serializers = [NoSerializer()]


def load_router(mapper):
    middlewares = get_middlewares()
    length = len(middlewares)
    router = _Router(mapper)
    for i in range(-1, -(length+1), -1):
        router = middlewares[i](router)
    return router


class Mapper(_Mapper):
    """The router map.

    If using the method, resource, not connect, please guarantee that the
    controller is wrapped by the class, Resource. Of couse, if using connect,
    it is not necessary.
    """
    def connect(self, *args, **kwargs):
        if "controller" in kwargs:
            c = kwargs["controller"]
            if not isinstance(c, Resource):
                kwargs["controller"] = Resource(c)
        return super(Mapper, self).connect(*args, **kwargs)


class Resource(object):
    def __init__(self, controller, serializers=_serializers):
        if isinstance(controller, strings):
            controller = __import__(controller)
            controller = controller()
        self.controller = controller

        if not isinstance(serializers, (list, tuple)):
            serializers = [serializers]
        self.serializers = serializers

    @dec.wsgify(RequestClass=Request)
    def __call__(self, request):
        action_args = self.get_action_args(request.environ)
        action = action_args.pop('action', None)
        try:
            result = {}
            for s in self.serializers:
                result = s.deserializer(request, result)
            action_args.update(result)
            action_result = self.dispatch(self.controller, action, request, **action_args)
            for s in self.serializers:
                action_result = s.serializer(action_result)
        except Exception as e:
            action_result = self.handle_exception(e)
        return action_result

    def dispatch(self, obj, action, *args, **kwargs):
        """Find action-specific method on self and call it."""
        try:
            method = getattr(obj, action)
        except AttributeError:
            method = getattr(obj, 'default')
        return method(*args, **kwargs)

    def get_action_args(self, request_environment):
        """Parse dictionary created by routes library."""
        try:
            args = request_environment['wsgiorg.routing_args'][1].copy()
        except Exception:
            return {}

        try:
            del args['controller']
        except KeyError:
            pass

        return args

    def handle_exception(self, exception):
        if hasattr(exception, "status"):
            return Response(status=exception.status)
        return Response(status=400)


class _Router(object):
    def __init__(self, mapper):
        #mapper.redirect("", "/")
        self._mapper = mapper
        self._router = middleware.RoutesMiddleware(self._dispatch, self._mapper)

    @dec.wsgify
    def __call__(self, req):
        return self._router

    @staticmethod
    @dec.wsgify
    def _dispatch(req):
        match = req.environ['wsgiorg.routing_args'][1]
        if not match:
            return webob.exc.HTTPNotFound()
        app = match['controller']
        return app
