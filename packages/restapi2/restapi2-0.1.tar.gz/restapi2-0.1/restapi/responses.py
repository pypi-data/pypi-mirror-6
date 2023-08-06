# coding: utf-8
from __future__ import absolute_import
import webob


class Response(webob.Response):
    pass


class Response100(Response):
    def __init__(self, *args, **kwargs):
        super(Response100, self).__init__(*args, **kwargs)
        self.status = 100


class Response101(Response):
    def __init__(self, *args, **kwargs):
        super(Response101, self).__init__(*args, **kwargs)
        self.status = 101


class Response102(Response):
    def __init__(self, *args, **kwargs):
        super(Response102, self).__init__(*args, **kwargs)
        self.status = 102


class Response200(Response):
    def __init__(self, *args, **kwargs):
        super(Response200, self).__init__(*args, **kwargs)
        self.status = 200


class Response201(Response):
    def __init__(self, *args, **kwargs):
        super(Response201, self).__init__(*args, **kwargs)
        self.status = 201


class Response202(Response):
    def __init__(self, *args, **kwargs):
        super(Response202, self).__init__(*args, **kwargs)
        self.status = 202


class Response203(Response):
    def __init__(self, *args, **kwargs):
        super(Response203, self).__init__(*args, **kwargs)
        self.status = 203


class Response204(Response):
    def __init__(self, *args, **kwargs):
        super(Response204, self).__init__(*args, **kwargs)
        self.status = 204


class Response205(Response):
    def __init__(self, *args, **kwargs):
        super(Response205, self).__init__(*args, **kwargs)
        self.status = 205


class Response206(Response):
    def __init__(self, *args, **kwargs):
        super(Response206, self).__init__(*args, **kwargs)
        self.status = 206


class Response207(Response):
    def __init__(self, *args, **kwargs):
        super(Response207, self).__init__(*args, **kwargs)
        self.status = 207


class Response226(Response):
    def __init__(self, *args, **kwargs):
        super(Response226, self).__init__(*args, **kwargs)
        self.status = 226


class Response300(Response):
    def __init__(self, *args, **kwargs):
        super(Response300, self).__init__(*args, **kwargs)
        self.status = 300


class Response301(Response):
    def __init__(self, *args, **kwargs):
        super(Response301, self).__init__(*args, **kwargs)
        self.status = 301


class Response302(Response):
    def __init__(self, *args, **kwargs):
        super(Response302, self).__init__(*args, **kwargs)
        self.status = 302


class Response303(Response):
    def __init__(self, *args, **kwargs):
        super(Response303, self).__init__(*args, **kwargs)
        self.status = 303


class Response304(Response):
    def __init__(self, *args, **kwargs):
        super(Response304, self).__init__(*args, **kwargs)
        self.status = 304


class Response305(Response):
    def __init__(self, *args, **kwargs):
        super(Response305, self).__init__(*args, **kwargs)
        self.status = 305


class Response307(Response):
    def __init__(self, *args, **kwargs):
        super(Response307, self).__init__(*args, **kwargs)
        self.status = 307


class Response400(Response):
    def __init__(self, *args, **kwargs):
        super(Response400, self).__init__(*args, **kwargs)
        self.status = 400


class Response401(Response):
    def __init__(self, *args, **kwargs):
        super(Response401, self).__init__(*args, **kwargs)
        self.status = 401


class Response402(Response):
    def __init__(self, *args, **kwargs):
        super(Response402, self).__init__(*args, **kwargs)
        self.status = 402


class Response403(Response):
    def __init__(self, *args, **kwargs):
        super(Response403, self).__init__(*args, **kwargs)
        self.status = 403


class Response404(Response):
    def __init__(self, *args, **kwargs):
        super(Response404, self).__init__(*args, **kwargs)
        self.status = 404


class Response405(Response):
    def __init__(self, *args, **kwargs):
        super(Response405, self).__init__(*args, **kwargs)
        self.status = 405


class Response406(Response):
    def __init__(self, *args, **kwargs):
        super(Response406, self).__init__(*args, **kwargs)
        self.status = 406


class Response407(Response):
    def __init__(self, *args, **kwargs):
        super(Response407, self).__init__(*args, **kwargs)
        self.status = 407


class Response408(Response):
    def __init__(self, *args, **kwargs):
        super(Response408, self).__init__(*args, **kwargs)
        self.status = 408


class Response409(Response):
    def __init__(self, *args, **kwargs):
        super(Response409, self).__init__(*args, **kwargs)
        self.status = 409


class Response410(Response):
    def __init__(self, *args, **kwargs):
        super(Response410, self).__init__(*args, **kwargs)
        self.status = 410


class Response411(Response):
    def __init__(self, *args, **kwargs):
        super(Response411, self).__init__(*args, **kwargs)
        self.status = 411


class Response412(Response):
    def __init__(self, *args, **kwargs):
        super(Response412, self).__init__(*args, **kwargs)
        self.status = 412


class Response413(Response):
    def __init__(self, *args, **kwargs):
        super(Response413, self).__init__(*args, **kwargs)
        self.status = 413


class Response414(Response):
    def __init__(self, *args, **kwargs):
        super(Response414, self).__init__(*args, **kwargs)
        self.status = 414


class Response415(Response):
    def __init__(self, *args, **kwargs):
        super(Response415, self).__init__(*args, **kwargs)
        self.status = 415


class Response416(Response):
    def __init__(self, *args, **kwargs):
        super(Response416, self).__init__(*args, **kwargs)
        self.status = 416


class Response417(Response):
    def __init__(self, *args, **kwargs):
        super(Response417, self).__init__(*args, **kwargs)
        self.status = 417


class Response418(Response):
    def __init__(self, *args, **kwargs):
        super(Response418, self).__init__(*args, **kwargs)
        self.status = 418


class Response422(Response):
    def __init__(self, *args, **kwargs):
        super(Response422, self).__init__(*args, **kwargs)
        self.status = 422


class Response423(Response):
    def __init__(self, *args, **kwargs):
        super(Response423, self).__init__(*args, **kwargs)
        self.status = 423


class Response424(Response):
    def __init__(self, *args, **kwargs):
        super(Response424, self).__init__(*args, **kwargs)
        self.status = 424


class Response426(Response):
    def __init__(self, *args, **kwargs):
        super(Response426, self).__init__(*args, **kwargs)
        self.status = 426


class Response500(Response):
    def __init__(self, *args, **kwargs):
        super(Response500, self).__init__(*args, **kwargs)
        self.status = 500


class Response501(Response):
    def __init__(self, *args, **kwargs):
        super(Response501, self).__init__(*args, **kwargs)
        self.status = 501


class Response502(Response):
    def __init__(self, *args, **kwargs):
        super(Response502, self).__init__(*args, **kwargs)
        self.status = 502


class Response503(Response):
    def __init__(self, *args, **kwargs):
        super(Response503, self).__init__(*args, **kwargs)
        self.status = 503


class Response504(Response):
    def __init__(self, *args, **kwargs):
        super(Response504, self).__init__(*args, **kwargs)
        self.status = 504


class Response505(Response):
    def __init__(self, *args, **kwargs):
        super(Response505, self).__init__(*args, **kwargs)
        self.status = 505


class Response507(Response):
    def __init__(self, *args, **kwargs):
        super(Response507, self).__init__(*args, **kwargs)
        self.status = 507


class Response510(Response):
    def __init__(self, *args, **kwargs):
        super(Response510, self).__init__(*args, **kwargs)
        self.status = 510
