import os
import re
import zlib
import json
import types
import random
import inspect
import logging
import mimetypes
from functools import partial, update_wrapper, wraps
from collections import Iterable
from urllib import parse
import http.client
from http.cookies import SimpleCookie
from cgi import FieldStorage, parse_header
from datetime import datetime

from jsonschema import validate
from jsonschema.exceptions import ValidationError, SchemaError

from biro import Router


class App:

    def __init__(self, name='klar_app'):
        self.name = name
        self.provider = Provider(
            cache=Cache,
            router=Router,
            rest=RestfulRouter,
            emitter=EventEmitter,
        )
        self.provide('req', Request, on_request=True)
        self.provide('res', Response, on_request=True)
        self.provide('cookies', Cookies, on_request=True)
        self.provide('session', Session, on_request=True)

        @self.provide('provider')
        def provider():
            return self.provider

        @self.provide('body', on_request=True)
        def body(req):
            return req.body

        @self.provide('uploads', on_request=True)
        def uploads(req):
            return req.uploads

        @self.provide('logger')
        def logger():
            l = logging.getLogger(name)
            l.setLevel(logging.DEBUG)
            return l

        self.provide('config', load_config)

        @self.provide('json_encoder')
        def json_encoder():
            return JSONEncoder

        def route(method, pattern, handler=None):
            if handler is None:
                return partial(self.provider.router.append, method, pattern)
            return self.provider.router.append(method, pattern, handler)

        for method in ['get', 'post', 'delete', 'put', 'patch', 'head']:
            m = partial(route, method.upper())
            m.__doc__ = """register a %(method)s handler

            Example:

                %(method)s('/path/<param>', handler)

                @%(method)s('/path/<param>')
                def handler(param):
                    pass
            """ % dict(method=method)
            setattr(self, method, m)

        self.resource = self.provider.rest.resource
        self.resources = self.provider.rest.resources

    def route(self, pattern, methods, handler=None):
        """register multiple routing rules

        Example:

             @route('/path/<param>', methods=['GET', 'POST'])
             def handler():
                 pass

        """
        if handler is None:
            return partial(self.route, pattern, methods)
        for method in methods:
            self.provider.router.append(method.upper(), pattern, handler)
        return handler

    def __call__(self, environ, start_response):
        return self.wsgi(environ, start_response)

    def wsgi(self, environ, start_response):
        self.provider.environ = environ
        res = self.provider.res
        try:
            self.process_request()
        except HttpError as e:
            res.code, res.body = e.args
        except Exception as e:
            res.code = 500
            self.provider.logger.error('Uncaught exception', exc_info=True)

        try:
            self.provider.emitter.emit(res.code)
            body, status, headers = res.output()
        except:
            self.provider.logger.error('Uncaught exception', exc_info=True)
            body, status, headers = '', '500 Internal Server Error', []

        if res.code != 500:
            if self.provider.accessed('session'):
                self.provider.session.flush()
            if self.provider.accessed('cookies'):
                cookies = self.provider.cookies.output()
                if cookies:
                    headers.extend(cookies)

        self.provider.reset_none_persist()

        start_response(status, headers)
        return [body]

    def process_request(self):
        res = self.provider.res
        handler, params = self.provider.router.match(
            self.provider.req.method, self.provider.req.path)
        if not handler:
            res.code = 404
            return

        params = dict(self.provider.req.query, **params)
        try:
            prepared_params = self.prepare_params(handler, params)
        except ValidationError as e:
            res.code = 400
            res.body = e.message
            return
        except SchemaError as e:
            self.provider.logger.error("Error in schema", exc_info=True)
            res.code = 500
            res.body = "Error in schema: %s" % e.message
            return

        res.from_handler(handler(**prepared_params))

        processers = handler.__annotations__.get('return')
        if processers is not None:
            if type(processers) is tuple:
                self.provider.res.pipe(*processers)
            else:
                self.provider.res.pipe(processers)

    def prepare_params(self, handler, params):
        args = inspect.getargs(handler.__code__)[0]
        params = dict(get_arg_defaults(handler), **params)
        for name in args:
            if hasattr(self.provider, name):
                params[name] = getattr(self.provider, name)

            if name not in params:
                if name in handler.__annotations__:
                    raise HttpError(400, "%s is required" % name)
                else:
                    raise HttpError(500, "can't provide %s" % name)

            if name in handler.__annotations__:
                anno = handler.__annotations__[name]
                if type(anno) is dict:
                    validate(params[name], anno)
                elif callable(anno):
                    params[name] = anno(params[name])
                else:
                    raise HttpError(500, "unrecognized annotation type for %s"
                                    % name)
        return {name: params[name] for name in args}

    def provide(self, name, component=None, on_request=False):
        if component is None:
            def decorate(fn):
                self.provider.register(name, fn, persist=not on_request)
                return fn
            return decorate
        else:
            self.provider.register(name, component, persist=not on_request)

    def on(self, event, handler=None):
        if handler:
            return self.provider.emitter.register(event, handler)
        else:
            return partial(self.provider.emitter.register, event)

    def run(self, port=3000):
        from wsgiref.simple_server import make_server
        self.provider.logger.info('listen on %s' % port)
        make_server('', port, self).serve_forever()

    def static(self, url_root, fs_root=None):
        if not url_root.endswith('/'):
            url_root = url_root + '/'
        if fs_root is None:
            fs_root = url_root[1:]
        self.provider.router.append('GET', re.compile(
            "^" + url_root + "(?P<url>.+)$"), static_handler(fs_root))

    def json_encode(self, t, encoder=None):
        """specify custom json encode method

        Example:

            @json_enocode(ObjectId)
            def encode_objectid(obj):
                return str(obj)
        """
        if encoder is None:
            return partial(self.json_encode, t)
        self.provider.json_encoder.add_encoder(t, encoder)

    def __repr__(self):
        return '<App %s>' % self.name

    def dump(self):
        print(repr(self.provider.router))


class Provider:

    def __init__(self, protos=None, **kwargs):
        self.protos = protos or kwargs
        self.__once__ = []

    def __getattr__(self, name):
        if name not in self.protos:
            raise AttributeError("%s not registered" % name)
        elif type(self.protos[name]) is tuple:
            cls, params = self.protos[name]
            self.__dict__[name] = instance(cls, params, self)
        elif isinstance(self.protos[name], type):
            self.__dict__[name] = instance(self.protos[name], self)
        else:
            self.__dict__[name] = invoke(self.protos[name], self)
        return self.__dict__[name]

    def __delattr__(self, name):
        if name in self.__dict__:
            del self.__dict__[name]

    def register(self, name, value, persist=True):
        self.protos[name] = value
        if not persist:
            self.__once__.append(name)

    def accessed(self, name):
        return name in self.__dict__

    def reset_none_persist(self):
        for name in self.__once__:
            if name in self.__dict__:
                del self.__dict__[name]


class cached_property:

    def __init__(self, fn):
        update_wrapper(self, fn)
        self.fn = fn

    def __get__(self, instance, cls):
        ret = instance.__dict__[self.fn.__name__] = self.fn(instance)
        return ret


class Request:

    def __init__(self, environ):
        self.environ = environ

    def env(self, key, default=None):
        return self.environ.get(key, default)

    def header(self, key, default=None):
        return self.environ.get('HTTP_' + key.replace('-', '_').upper(),
                                default)

    @cached_property
    def content_type(self):
        return parse_header(self.environ['CONTENT_TYPE'])

    @cached_property
    def content_length(self):
        return int(self.environ['CONTENT_LENGTH'])

    @cached_property
    def query(self):
        return dict(parse.parse_qsl(self.environ['QUERY_STRING']))

    @cached_property
    def body(self):
        if not hasattr(self, '_body'):
            self.parse_body()
        return self._body

    def parse_body(self):
        content_type, _ = self.content_type
        if content_type == 'application/json':
            self._body = json.loads(self.get_raw_body())
        elif content_type == 'application/x-www-form-urlencoded':
            self._body = dict(parse.parse_qsl(self.get_raw_body()))
        elif content_type == 'multipart/form-data':
            fs = FieldStorage(self.environ['wsgi.input'], environ=self.environ)
            self._body, self._uploads = {}, {}
            for name in fs.keys():
                if fs[name].filename is None:
                    self._body[name] = fs[name].value
                else:
                    self._uploads[name] = fs[name]

    def get_raw_body(self):
        content_length = int(self.environ.get('CONTENT_LENGTH', 0))
        if content_length == 0:
            return ''
        return self.environ['wsgi.input'].read(content_length).decode()

    @cached_property
    def uploads(self):
        if not hasattr(self, '_uploads'):
            self.parse_body()
        return self._uploads

    @cached_property
    def path(self):
        return self.environ['PATH_INFO']

    @cached_property
    def method(self):
        return self.environ['REQUEST_METHOD'].upper()

    @cached_property
    def is_ajax(self):
        return self.environ.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


class Cookies:

    units = {
        "day": 86400,
        "days": 86400,
        "hour": 3600,
        "hours": 3600,
        "minute": 60,
        "minutes": 60,
    }

    def __init__(self, environ):
        self.cookies = SimpleCookie()
        if 'HTTP_COOKIE' in environ:
            self.cookies.load(environ['HTTP_COOKIE'])
        self.changed_keys = []

    def get(self, key, default=None):
        return self.cookies[key].value if key in self.cookies else default

    def set(self, key, value, **kwargs):
        self.cookies[key] = value
        for k, v in kwargs.items():
            self.cookies[key][k] = v
        self.changed_keys.append(key)

    def __getattr__(self, key):
        if key.startswith('set_for_'):
            tokens = iter(key[8:].split('_'))
            total = 0
            for quantity, unit in zip(tokens, tokens):
                total += int(quantity) * self.units[unit]
            return partial(self.set, expires=int(total))
        else:
            raise HttpError(500, '%s not exists' % key)

    def delete(self, key):
        if key in self.cookies:
            self.set(key, '', expires='Thu, 01 Jan 1970 00:00:00 GMT')

    def output(self):
        return [('Set-Cookie', self.cookies[key].OutputString())
                for key in self.cookies if key in self.changed_keys]


class Session:

    chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

    def __init__(self, cookies, cache, sid_key='ksid', key_len=16,
                 key_prefix='sid:'):
        self.cache = cache
        self.cookies = cookies
        self.sid_key = sid_key
        self.key_len = key_len
        self.key_prefix = key_prefix

        sid = self.cookies.get(sid_key)
        self.data = {}
        if sid and self.load(sid):
            self._sid = sid
        self.is_dirty = False

    @property
    def sid(self):
        if not hasattr(self, '_sid'):
            self._sid = ''.join(random.choice(self.chars)
                                for i in range(self.key_len))
            self.cookies.set(self.sid_key, self._sid, httponly=True)
        return self._sid

    def load(self, sid):
        data = self.cache.get(self.key_prefix + sid)
        if data and type(data) is not dict:
            try:
                if type(data) is not str:
                    data = data.decode()
                data = json.loads(data)
            except:
                raise Exception("Failed to unserialize session data")
        self.data = data or {}
        return data

    def get(self, key, default=None):
        return self.data[key] if key in self.data else default

    def set(self, key, value):
        self.is_dirty = True
        self.data[key] = value

    def delete(self, key):
        if key in self.data:
            self.is_dirty = True
            del self.data[key]

    def destroy(self):
        self.data = {}
        self.cache.delete(self.key_prefix + self.sid)
        self.cookies.delete(self.sid_key)
        self.is_dirty = False

    def flush(self):
        if self.is_dirty:
            try:
                data = json.dumps(self.data)
            except:
                raise Exception("Failed to serialize session data")
            self.cache.set(self.key_prefix + self.sid, data)
            self.is_dirty = False


class Cache:
    "should not be use in production"

    def get(self, key):
        return self.__dict__.get(key)

    def set(self, key, value):
        self.__dict__[key] = value

    def delete(self, key):
        del self.__dict__[key]


class EventEmitter:

    def __init__(self, provider):
        self.listeners = {}
        self.provider = provider

    def emit(self, event, **kargs):
        if event in self.listeners:
            for listener in self.listeners[event]:
                invoke(listener, kargs, self.provider)

    def register(self, event, handler):
        if event in self.listeners:
            self.listeners[event].append(handler)
        else:
            self.listeners[event] = [handler]


class HttpError(Exception):
    pass


class RestfulRouter:

    restful_routes = [
        ('GET',    '%(path)s',               'query'),
        ('POST',   '%(path)s',               'create'),
        ('GET',    '%(path)s/<%(id)s>',      'show'),
        ('PUT',    '%(path)s/<%(id)s>',      'replace'),
        ('PATCH',  '%(path)s/<%(id)s>',      'modify'),
        ('DELETE', '%(path)s/<%(id)s>',      'destroy'),
        ('GET',    '%(path)s/new',           'new'),
        ('GET',    '%(path)s/<%(id)s>/edit', 'edit'),
    ]

    def __init__(self, router):
        self.router = router

    def resource(self, url_path=None, module=None):
        """register a restful resource

        Example:

            @resource('/article')
            class Article:
                def show(article_id):
                    pass

                @method('put')
                def upvote(article_id):
                    pass

        """
        if url_path is None:
            url_path = '/' + module.__name__.replace('.', '/')
        if module is None:
            return partial(self.register_resource, url_path)
        else:
            return self.register_resource(url_path, module)

    def resources(self, *resources, prefix=''):
        """register a list of restful resources

        Example:

            resources(articles, users, '/api/v1')

        """
        for resource in resources:
            url_path = prefix + '/' + resource.__name__.split('.').pop()
            self.register_resource(url_path, resource)

    def register_resource(self, url_path, module):
        url_id = '%s_id' % url_path.split('/').pop()
        vals = {'path': url_path, 'id': url_id}
        rules = [(method, pattern % vals, getattr(module, handler))
                 for method, pattern, handler in self.restful_routes
                 if hasattr(module, handler)]

        if isinstance(type(module), types.ModuleType):
            fns = get_module_fns(module)
        else:
            fns = get_methods(module)

        custom_rules = [(fn.__httpmethod__,
                         '%s/<%s>/%s' % (url_path, url_id, fn.__name__),
                        fn) for fn in fns]
        self.router.extend(rules)
        self.router.extend(custom_rules)
        return module


class Response:

    def __init__(self, json_encoder, environ, provider):
        self.body = None
        self.code = 200
        self.headers = {}
        self.json_encoder = json_encoder
        self.environ = environ
        self.provider = provider

    def output(self):
        headers = {'Content-Type': 'text/html; charset=utf-8'}
        body = '' if self.body is None else self.body
        code = self.code
        if type(body) not in [str, bytes]:
            body = json.dumps(body, cls=self.json_encoder)
            headers = {'Content-Type': 'application/json; charset=utf-8'}
        headers.update(self.headers)
        if self.code == 200 and is_fresh(self.environ, headers):
            code, body = 304, ''
        if type(body) is str:
            body = body.encode('utf-8')
        return body, get_status(code), list(headers.items())

    def pipe(self, *processers):
        for processer in processers:
            args = get_args(processer)
            if len(args) == 1 and args[0] != 'res':
                self.body = processer(self.body)
            else:
                invoke(processer, self.provider)
        return self

    def from_handler(self, response):
        if isinstance(response, tuple):
            for item in response:
                if type(item) is tuple:
                    key, value = item
                    self.headers[key] = value
                elif type(item) is int:
                    self.code = item
                else:
                    self.body = item
        elif type(response) is int:
            self.code = response
        else:
            self.body = response

    def header(self, key, value):
        self.headers[key] = value


class JSONEncoder(json.JSONEncoder):

    __custom_encoders__ = {}

    @classmethod
    def add_encoder(self, t, encode):
        self.__custom_encoders__[t] = encode

    def default(self, obj):
        for t in self.__custom_encoders__:
            if isinstance(obj, t):
                return self.__custom_encoders__[t](obj)
        if isinstance(obj, Iterable):
            return list(obj)
        return super().default(obj)


def invoke(fn, *param_dicts):
    "call a function with a list of dicts providing params"
    prepared_params = {}
    args = get_args(fn)
    defaults = get_arg_defaults(fn)
    for name in args:
        for params in param_dicts:
            if type(params) is dict and name in params:
                prepared_params[name] = params[name]
                break
            elif hasattr(params, name):
                prepared_params[name] = getattr(params, name)
                break
        if name not in prepared_params:
            if name in defaults:
                prepared_params[name] = defaults[name]
            else:
                raise Exception("%s is required" % name)
    return fn(**prepared_params)


def instance(cls, *param_dicts):
    "get instance of a given class"
    if isinstance(cls.__init__, types.FunctionType):
        return invoke(cls, *param_dicts)
    else:
        return cls()


def get_arg_defaults(fn):
    "get arguments with default values as a dict"
    sig = inspect.signature(fn)
    return {p.name: p.default for p in sig.parameters.values()
            if p.kind is p.POSITIONAL_OR_KEYWORD and p.default is not p.empty}


def get_args(fn):
    "get argument names of a function as a list of strings"
    sig = inspect.signature(fn)
    return [p.name for p in sig.parameters.values()
            if p.kind is p.POSITIONAL_OR_KEYWORD]


def get_status(code):
    "get status using http code"
    if code not in http.client.responses:
        raise HttpError(500, '%s is not a valide status code' % code)
    return "%s %s" % (code, http.client.responses[code])


def redirect(url, permanent=False):
    code = 301 if permanent else 302
    return code, ('Location', url)


def static_handler(fs_root):
    if not os.path.isdir(fs_root):
        raise HttpError(500, "static root %s should be a dir" % fs_root)

    def handler(url) -> etag:
        fs_path = os.path.join(fs_root, url)
        if not os.path.isfile(fs_path):
            return 404, "%s not exists" % fs_path
        mime = mimetypes.guess_type(fs_path)[0] or 'application/octet-stream'
        with open(fs_path) as fp:
            content = fp.read()
        return content, ('Content-Type', mime)
    return handler


def load_config(logger):
    path = os.environ.get('CONFIG') or "config.py"
    if os.path.isfile(path):
        import imp
        mod = imp.load_source(path[:-3], '%s' % path)
        return {k: getattr(mod, k) for k in dir(mod) if not k.startswith('_')}
    else:
        logger.warn("failed to load config %s" % path)
        return {}


def etag(res):
    "add Etag to response header if response code is 200"
    if res.code == 200 and res.body:
        res.headers['Etag'] = "%X" % (zlib.crc32(bytes(res.body, "utf-8"))
                                      & 0xFFFFFFFF)


_etag_delimiter = re.compile(' *, *')


def is_fresh(request_headers, response_headers):
    last_modified = response_headers.get('Last-Modified')
    if last_modified:
        fmt = "%a, %d %b %Y %H:%M:%S GMT"
        response_headers['Last-Modified'] = last_modified.strftime(fmt)
        modified_since = request_headers.get('HTTP_IF_MODIFIED_SINCE')
        if modified_since:
            try:
                modified_since = datetime.strptime(modified_since, fmt)
                if modified_since < last_modified:
                    return True
            except:
                pass
    etag = response_headers.get('Etag')
    etags = request_headers.get('HTTP_IF_NONE_MATCH')
    if etag and etags:
        etags = _etag_delimiter.split(etags)
        if etags:
            return etags[0] == '*' or etag in etags


def get_module_fns(module):
    "get request handlers of a module"
    attrs = [getattr(module, a) for a in dir(module) if not a.startswith('_')]
    return [attr for attr in attrs if isinstance(attr, types.FunctionType)
            and hasattr(attr, '__httpmethod__')]


def get_methods(cls):
    "get request handlers of a class"
    attrs = [getattr(cls, a) for a in dir(cls) if not a.startswith('_')]
    return [attr for attr in attrs if isinstance(attr, types.FunctionType)
            and hasattr(attr, '__httpmethod__')]


def method(httpmethod):
    """decorator to overwrite default method(GET) for custom actions,
    intended to be used within restful resource
    """
    def add_method(fn):
        fn.__httpmethod__ = httpmethod.upper()
        return fn
    return add_method


def cache_control(*args, **kwargs):
    """decorator to specify Cache-Control header

    Example:

        @get('/')
        @cache_control('public', max_age=60)
        def home():
            pass
    """
    def decorator(handler):
        @wraps(handler)
        def wrapper(*a, **k):
            value = args + tuple(['%s=%s' % i for i in kwargs.items()])
            response = handler(*a, **k)
            header = 'Cache-Control', ', '.join(value).replace('_', '-')
            if response:
                if type(response) is tuple:
                    return response + (header,)
                else:
                    return (response, header)
            return (header,)
        return wrapper
    return decorator


def env(enviroment, fn=None):
    """run conditional code for specified enviroment read from $KLAR_ENV

    Example:

        @env('production')
        def config_for_production():
            @app.provide('db')
            def db():
                pass
    """
    if fn is None:
        return partial(env, enviroment)
    if os.environ.get('KLAR_ENV') == enviroment:
        fn()
    return fn
