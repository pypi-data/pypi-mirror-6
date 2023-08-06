# coding: utf-8
from __future__ import absolute_import
import json
from .interfaces import Serializer


class NoSerializer(Serializer):
    pass


class JSONSerializer(Serializer):
    """Serializer the body from the json bytes to the python object,
    or from the python object to the json bytes. The python object may be a dict
    or list."""

    def update(self, new, old):
        if new:
            if old:
                return old.update(new)
            return new
        return old

    def serializer(self, response):
        return json.dumps(response)

    def deserializer(self, request, result=None):
        data = json.loads(request.body)
        return self.update(data, result)
