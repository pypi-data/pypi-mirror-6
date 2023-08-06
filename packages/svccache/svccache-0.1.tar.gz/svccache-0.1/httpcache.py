"""
A simple http cache that listens to cache invalidation messages.

TODO:
- cache invalidation
- look at handling standard headers like If-Modified-Since and
ETag and what not (research).
- potentially develop other headers.
- SSL and client cert support.

"""

import tornado.web
import tornado.httpclient
from tornado import gen

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

import time


_DEFAULT_MAX_TTL = 3600 * 24 * 365


class CacheSvc(tornado.web.Application):
    def __init__(self, **options):
        """Create new cache service. Requires the following options:
        - driver: the cache driver to use.
        - driver_options: driver-specific options.
        - upstream: authoritative source for http requests.
        - message_source: where to connect for cache control messages.
        """
        logger.debug('CacheSvc starting for ' + options['upstream'] + '...')
        handlers = [
            (r"/_status", StatusHandler),
            (r"/.*", ProxyHandler)
            ]
        tornado_app_settings = {}
        super(CacheSvc, self).__init__(handlers, **tornado_app_settings)

        self._setoptions(options)
        self._init_cache()

    def _setoptions(self, options):
        class Options:
            pass
        self.options = Options()
        self.options.upstream = normalize_url(options['upstream'])

    def _init_cache(self):
        # TODO: use driver and options
        import lrucache
        self._cache = lrucache.FixedSizeLRUCache()

def normalize_url(url):
    # TODO
    return url

class BaseHandler(tornado.web.RequestHandler):
    def upstream_url(self, uri):
        "Returns the URL to the upstream data source for the given URI based on configuration"
        return self.application.options.upstream + self.request.uri

    def set_headers(self, headers):
        for (name, value) in headers.iteritems():
            self.set_header(name, value)

    def cache_get(self):
        "Returns (headers, body) from the cache or raise KeyError"
        key = self.cache_key()
        (headers, body, expires_ts) = self.application._cache[key]
        if expires_ts < time.now():
            # asset has expired, delete it
            del self.application._cache[key]
            raise KeyError(key)

        return (headers, body)

    def cache_put(self, headers, body, ttl_sec):
        if ttl_sec <= 0: return
        expires_ts = time.time() + ttl_sec
        self.application._cache[self.cache_key()] = (headers, body, expires_ts)

    def cache_key():
        return (self.request.method, self.request.uri)

class StatusHandler(BaseHandler):
    def get(self):
        # TODO: expand on status, include some metrics
        self.write("{'status': 'ok'}")

class ProxyHandler(BaseHandler):
    @gen.coroutine
    def get(self):
        try:
            (headers, body) = self.cache_get()
            logger.debug('cache hit for ' + self.request.uri)
            self.set_headers(headers)
            self.write(body)
        except KeyError:
            logger.debug('cache miss for ' + self.request.uri)
            # Not in cache. Get it from server and cache it...
            upstream_request = self.make_upstream_request()
            logger.debug(upstream_request.method + ' ' + upstream_request.url \
                        + ' ' + str(self.request.headers))
            http_client = tornado.httpclient.AsyncHTTPClient()
            try:
                response = yield http_client.fetch(upstream_request)
            except tornado.httpclient.HTTPError, e:
                response = e.response

            self.cache_put(response.headers, response.body, self.ttl(response))

            # TODO: If-None-Match: "..."
            # code 304

            self.set_status(response.code)
            self.set_headers(response.headers)
            self.write(response.body)

    def make_upstream_request(self):
        "Return request object for calling the upstream"
        url = self.upstream_url(self.request.uri)
        return tornado.httpclient.HTTPRequest(url,
            method=self.request.method,
            headers=self.request.headers,
            body=self.request.body if self.request.body else None)

    def ttl(self, response):
        """Returns time to live in seconds. 0 means no caching.

        Criteria:
        - response code 200
        - read-only method (GET, HEAD, OPTIONS)
        Plus http headers:
        - cache-control: option1, option2, ...
          where options are:
          private | public
          no-cache
          no-store
          max-age: seconds
          s-maxage: seconds
          must-revalidate
          proxy-revalidate
        - expires: Thu, 01 Dec 1983 20:00:00 GMT
        - pragma: no-cache (=cache-control: no-cache)

        See http://www.mobify.com/blog/beginners-guide-to-http-cache-headers/

        TODO: tests

        """
        if response.code != 200: return 0
        if not self.request.method in ['GET', 'HEAD', 'OPTIONS']: return 0

        try:
            pragma = self.request.headers['pragma']
            if pragma == 'no-cache':
                return 0
        except KeyError:
            pass

        try:
            cache_control = self.request.headers['cache-control']

            # no caching options
            for option in ['private', 'no-cache', 'no-store', 'must-revalidate', 'proxy-revalidate']:
                if cache_control.find(option): return 0

            # further parsing to get a ttl
            options = parse_cache_control(cache_control)
            try:
                return int(options['s-maxage'])
            except KeyError:
                pass
            try:
                return int(options['max-age'])
            except KeyError:
                pass

            if 's-maxage' in options:
                max_age = options['s-maxage']
                if max_age < ttl: ttl = max_age
            if 'max-age' in options:
                max_age = options['max-age']
                if max_age < ttl: ttl = max_age
            return ttl
        except KeyError:
            pass

        try:
            expires = self.request.headers['expires']
            return time.mktime(time.strptime(expires, '%a, %d %b %Y %H:%M:%S')) - time.time()
        except KeyError:
            pass


def parse_cache_control(cache_control):
    #return dict([(split[0], split[1] if len(split) > 1 else '') for split in [item.split(': ') for item in cache_control.split(', ')]])
    items = cache_control.split(', ')
    splits = [item.split(': ') for item in items]
    pairs = [(split[0], split[1] if len(slit) > 1 else '') for split in splits]
    return dict(pairs)

import tornado.ioloop
import tornado.web
import tornado.httpserver

from tornado.options import define, options
define("port", default=8887, help="run on the given port (default 8887)", type=int)
define("upstream", help="specify upstream url")

def main():
    tornado.options.parse_command_line()
    service = CacheSvc(upstream=options.upstream)
    http_server = tornado.httpserver.HTTPServer(service)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()


