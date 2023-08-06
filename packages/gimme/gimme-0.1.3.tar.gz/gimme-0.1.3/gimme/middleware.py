import abc
import re
import os
import sys
import random
import uuid
import json as jsonlib
from dogpile.cache import make_region
from dogpile.cache.api import NO_VALUE
from .parsers.multipart import MultipartParser
from .dotdict import DotDict
from .ext.session import Session as Session
from .errors import AbortRender
from jinja2 import Environment, PackageLoader, ChoiceLoader, FileSystemLoader


class Middleware(object):
    def __init__(self, app, request, response):
        self.app = app
        self.request = request
        self.response = response

    def __enter__(self):
        if not self.response._aborted:
            try:
                return self.enter()
            except AbortRender:
                self.response._aborted = True

    def __exit__(self, err_type, err_obj, traceback):
        if not self.response._aborted:
            self.exit_arguments = (err_type, err_obj, traceback)
            try:
                self.exit()
            except AbortRender:
                self.response._aborted = True

        if isinstance(err_obj, AbortRender):
            self.response._aborted = True

    def enter(self):
        pass

    def exit(self):
        pass


def connection_helper(connection='close'):
    class ConnectionHelperMiddleware(Middleware):
        def exit(self):
            self.response.headers['Connection'] = connection
            self.response.headers['Content-Length'] = str(len(
                self.response.body))

    return ConnectionHelperMiddleware


def static(path, expose_as='/'):
    import mimetypes

    expose_as = (expose_as or os.path.basename(path)).strip('/')
    pattern = re.compile('^/%s.*' % re.escape(expose_as))
    mimetypes.init()

    class StaticMiddleware(Middleware):
        def enter(self):
            match = pattern.match(self.request.headers.path_info)
            local_path = None

            if match:
                local_path = self._get_local_path(
                    self.request.headers.path_info)
                if local_path:
                    self.response.set('Content-Type', mimetypes.guess_type(
                        local_path)[0])
                    self.response.status = 200
                    try:
                        with open(local_path, 'r') as f:
                            self.response.body = f.read()
                    except OSError, e:
                        pass
                    finally:
                        raise AbortRender

        def _get_local_path(self, local_path):
            local_path = local_path.strip('/')[len(expose_as):].lstrip('/')
            temp_path = os.path.join(path, local_path)
            if temp_path.startswith(path) and os.path.isfile(temp_path):
                return temp_path
            else:
                return None

    return StaticMiddleware


def cookie_parser():
    class CookieParserMiddleware(Middleware):
        def enter(self):
            try:
                data = self.request.cookies.split('; ')
            except AttributeError:
                self.request.cookies = DotDict()
                return

            self.request.cookies = DotDict()
            for i in data:
                if i:
                    split = i.split('=', 1)
                    if split:
                        self.request.cookies[split[0]] = split[1]

    return CookieParserMiddleware


def session(cache='gimme.cache.memory', session_cookie='gimme_session',
        make_session_key=uuid.uuid4, expiration_time=60*60*24*7, **kwargs):

    region = make_region().configure(cache,
        expiration_time=expiration_time, **kwargs)

    class SessionMiddleware(Middleware):
        def enter(self):
            self.request.session = self._load_session()

        def exit(self):
            if self.request.session._state.is_dirty():
                self.request.session.save()

        def _load_session(self):
            try:
                key = self.request.cookies[session_cookie]
            except KeyError:
                return self._create_session()

            session_data = region.get(key)

            if session_data != NO_VALUE:
                return Session(region, key, session_data)
            else:
                return self._create_session()

        def _create_session(self):
            key = str(make_session_key())
            self.response.set('Set-Cookie', '%s=%s' % (session_cookie, key))
            new_session = Session(region, key, {}, True)
            return new_session

    return SessionMiddleware


def json():
    class JsonMiddleware(Middleware):
        def enter(self):
            if not hasattr(self.request, 'body'):
                self.request.body = DotDict()
     
            if self.request.type == 'json':
                try:
                    parsed_data = jsonlib.loads(self.request.raw_body)
                except ValueError:
                    pass
                else:
                    for k, v in parsed_data.iteritems():
                        self.request.body[k] = v

    return JsonMiddleware


def urlencoded():
    from .uri import QueryString

    class URLEncodedMiddleware(Middleware):
        def enter(self):
            if not hasattr(self.request, 'body'):
                self.request.body = DotDict()
     
            if self.request.type == 'application/x-www-form-urlencoded':
                qs = QueryString(self.request.raw_body)
                for k, v in qs.iteritems():
                    self.request.body[k] = v

    return URLEncodedMiddleware


def multipart():
    multipart_pattern = re.compile('^multipart/form-data; boundary=(.*)', re.I)

    class MultipartMiddleware(Middleware):
        def enter(self):
            if not hasattr(self.request, 'body'):
                self.request.body = DotDict()

            if not hasattr(self.request, 'files'):
                self.request.files = DotDict()
                
            if ('content_type' in self.request.headers and
                    'request_method' in self.request.headers and
                    self.request.headers.request_method in ('PUT', 'POST')):

                match = multipart_pattern.match(
                    self.request.headers.content_type)

                if match:
                    mp = MultipartParser(match.group(1), self.request.wsgi.input)
                    for name, mp_file in mp.iteritems():
                        if mp_file.value:
                            self.request.body[name] = mp_file.value
                        else:
                            self.request.files[name] = mp_file

    return MultipartMiddleware


def body_parser(json_args={}, urlencoded_args={}, multipart_args={}):
    json_parser = json(**json_args)
    urlencoded_parser = urlencoded(**urlencoded_args)
    multipart_parser = multipart(**multipart_args)

    class BodyParserMiddleware(Middleware):
        def enter(self):
            json_parser(self.app, self.request, self.response).enter()
            urlencoded_parser(self.app, self.request, self.response).enter()
            multipart_parser(self.app, self.request, self.response).enter()

    return BodyParserMiddleware


def method_override():
    from .uri import QueryString

    multipart_pattern = re.compile('^multipart/form-data; boundary=(.*)', re.I)

    class MethodOverrideMiddleware(Middleware):
        def enter(self):
            if self.request.type == 'application/x-www-form-urlencoded':
                query_string = self.QueryString(self.request.raw_body)
                if '_method' in query_string:
                    self.request.headers.request_method = query_string._method

    return MethodOverrideMiddleware


def compress():
    import zlib

    class CompressMiddleware(Middleware):
        def exit(self):
            if 'accept_encoding' in self.request.headers:
                    if ('deflate' in
                            self.request.headers.accept_encoding.split(',')):
                        try:
                            compressed = zlib.compress(self.response.body)
                        except TypeError:
                            pass
                        else:
                            self.response.headers['Content-Encoding'] = 'deflate'
                            self.response.headers['Content-Length'] = str(
                                len(compressed))
                            self.response.body = compressed

    return CompressMiddleware


def profiler(fn=None, pr=None):
    import cProfile

    class ProfilerMiddleware(Middleware):
        def enter(self):
            if pr is None:
                pr = cProfile.Profile()

            pr.enable()

        def exit(self):
            pr.disable()
            if fn:
                fn(pr)

    return ProfilerMiddleware
