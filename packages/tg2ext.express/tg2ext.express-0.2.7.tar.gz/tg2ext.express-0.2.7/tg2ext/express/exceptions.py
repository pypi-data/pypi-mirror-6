# -*- coding: utf-8 -*-
from webob.exc import WSGIHTTPException
from webob.request import Request
from webob.response import Response
try:
    import simplejson as json
except:
    import json


class ExpressError(WSGIHTTPException):
    ## You should set in subclasses:
    # code = 200
    # title = 'OK'
    # explanation = 'why this happens'
    code = 500
    title = U"Unknown Error!"
    explanation = U''

    ## Set this to True for responses that should have no request body
    empty_body = False

    def __init__(self, detail=None, headers=None, title=None, comment=None, explanation=None, **kw):
        Response.__init__(self,
                          status='%s %s' % (self.code, self.title),
                          **kw)
        Exception.__init__(self, detail)
        if headers:
            self.headers.extend(headers)
        self.title = title or self.title
        self.detail = detail
        self.comment = comment
        self.explanation = explanation or self.explanation
        if self.empty_body:
            del self.content_type
            del self.content_length

    def _make_body(self, environ, escape):
        result = {'code': self.code,
                  'title': self.title,
                  'explanation': self.explanation,
                  'detail': self.detail or '',
                  'comment': self.comment or '',
                  }

        return json.dumps(result)

    def plain_body(self, environ):
        return self._make_body(environ, None)

    def html_body(self, environ):
        return self._make_body(environ, None)

    def generate_response(self, environ, start_response):
        if self.content_length is not None:
            del self.content_length
        headerlist = list(self.headerlist)
        accept = environ.get('HTTP_ACCEPT', '')
        if accept and 'json' in accept or '*/*' in accept:
            content_type = 'application/json'
            body = self.html_body(environ)
        else:
            content_type = 'text/plain'
            body = self.plain_body(environ)
        extra_kw = {}
        resp = Response(body,
                        status=self.status,
                        headerlist=headerlist,
                        content_type=content_type,
                        **extra_kw)
        resp.content_type = content_type
        return resp(environ, start_response)

    def __call__(self, environ, start_response):
        is_head = environ['REQUEST_METHOD'] == 'HEAD'
        if self.body or self.empty_body or is_head:
            app_iter = Response.__call__(self, environ, start_response)
        else:
            app_iter = self.generate_response(environ, start_response)
        if is_head:
            app_iter = []
        return app_iter

    @property
    def wsgi_response(self):
        return self

    def __repr__(self):
        return "<%s: %d (%s)>: %s" % (self.__class__.__name__, self.code, self.title, self.detail)

    def __unicode__(self):
        return u"<%s: %d (%s)>: %s" % (self.__class__.__name__, self.code, self.title, self.detail)


class ServerFault(ExpressError):
    code = 500
    title = "Server Fault!"


class FatalError(ExpressError):
    code = 501
    title = "Fatal Error!"


class BadRequest(ExpressError):
    code = 400
    title = "Bad Request!"


class InvalidExpression(ExpressError):
    code = 400
    title = "Invalid Expression!"


class NotFound(ExpressError):
    code = 404
    title = "Object Not Found!"


class InvalidData(ExpressError):
    code = 400
    title = "Invalid Data!"


class Forbidden(ExpressError):
    code = 403
    title = "Access Forbidden!"


class Unauthorized(ExpressError):
    code = 401
    title = "Unauthorizes Access!"


__all__ = ['ExpressError', 'BadRequest', 'InvalidExpression', 'InvalidData', 'NotFound',
           'FatalError', 'ServerFault', 'Forbidden', 'Unauthorized']