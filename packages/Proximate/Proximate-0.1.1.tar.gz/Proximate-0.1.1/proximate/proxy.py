#!/usr/bin/env python

"""
Simple HTTP Reverse Proxy that emulates the behavior of Apache's ProxyPass
by aggregating multiple hosts into a unified namespace.
Very useful for JavaScript's Single-Origin Policy.
"""

# TODO: use wsgiref instead of Paste. Or Werkzeug's run_simple
# TODO: run http://docs.python.org/2/library/wsgiref.html#wsgiref.validate.validator

import argparse
import logging
import urlparse

from paste import httpserver
from wsgiproxy.app import WSGIProxyApp

class Route(object):
    """
    Routes all requests for a path to a remote url.

    :param path: A path to match, which should start and end with '/'.

    :param remote_url: Where matching requests should be sent.
    """
    def __init__(self, path, remote_url, proxy_url):
        self.path       = path
        self.remote_url = remote_url
        self.proxy_url  = proxy_url
        self.app        = WSGIProxyApp(remote_url)

    def match(self, environ, start_response):
        match = environ['PATH_INFO'].startswith(self.path)
        if match:
            logging.info("Match: path_info='%s', path='%s', remote_url='%s'",
                         environ['PATH_INFO'], self.path, self.remote_url)
        return match

    # Simplified from wsgifilter.filter
    # See also http://wsgi.readthedocs.org/en/latest/specifications/avoiding_serialization.html
    def application(self, environ, start_response):
        """Subsidiary WSGI application which proxies to `remote_url`
        and filters the output, making it appear as if it came
        from this host."""
        captured = []
        written_output = []

        def replacement_start_response(
                status, response_headers, exc_info=None):
            captured[:] = [status, response_headers]
            return written_output.append # WSGI legacy write callable

        self.strip_path_prefix(environ)
        self.prepare_environ(environ)

        # Make proxied request
        app_iter = self.app(environ, replacement_start_response)
        app_iter = self.handle_weird_apps(app_iter, captured, written_output)

        # Filter the response
        try:
            return self.filter_output(
                environ, start_response, captured[0], captured[1], app_iter)
        finally:
            if hasattr(app_iter, 'close'):
                app_iter.close()

    def strip_path_prefix(self, environ):
        old_path = environ['PATH_INFO']
        assert old_path.startswith(self.path)
        prefix_len = len(self.path) - (1 if self.path.endswith('/') else 0)
        new_path = old_path[prefix_len:]
#       logging.debug("'%s' -> '%s'", old_path, new_path)
        assert new_path.startswith('/')
        environ['PATH_INFO'] = new_path
        return (old_path, new_path)

    def prepare_environ(self, environ):
        # WSGIProxyApp sets multiple X-Forwarded-* headers
        # but not X-Forwarded-Host. However, werkzeug.wsgi.get_host()
        # looks at X-Forwarded-Host to construct the canonical hostname.
        # See http://httpd.apache.org/docs/2.2/mod/mod_proxy.html#x-headers
        environ['HTTP_X_FORWARDED_HOST'] = environ['HTTP_HOST']

    def handle_weird_apps(self, app_iter, captured, written_output):
        if not captured or written_output:
            # This app hasn't called start_response. We can't do
            # anything magic with it; or it used the start_response
            # WRITER, and we still can't do anything with it
            try:
                for chunk in app_iter:
                    written_output.append(chunk)
            finally:
                if hasattr(app_iter, 'close'):
                    app_iter.close()
            app_iter = written_output
        return app_iter

    def filter_output(
            self, environ, start_response, status,
            response_headers, app_iter):
        start_response(
            status,
            self.rewrite_response_headers(response_headers))
        return self.rewrite_response_data(app_iter)

    def rewrite_response_headers(self, response_headers):
        new_headers = []
        for name, value in response_headers:
            if name.lower() == 'location':
                value = self.rewrite_href(value)
            # TODO: Set-Cookie domain?
            new_headers.append((name, value))
        return new_headers

    def rewrite_href(self, target_url):
        rewritten_url = target_url.replace(self.remote_url, self.proxy_url)
#       logging.info(
#           "rewrite_href: proxy_url='%s', path='%s', remote_url='%s', target_url='%s' -> %s",
#           self.proxy_url, self.path, self.remote_url, target_url, rewritten_url)
        return rewritten_url

    def rewrite_response_data(self, app_iter):
        # TODO: rewrite URLs in HTML and CSS?
#       data = ''.join(app_iter)
        return app_iter


class Router(object):
    """
    Manages a sequence of Routes.
    """
    def __init__(self, ordered_rules, proxy_url):
        self.ordered_routes = [Route(path, url, proxy_url)
                               for path, url in ordered_rules]
        self.proxy_url = proxy_url

    def __call__(self, environ, start_response):
#       logging.info("Got: '%s'", environ['PATH_INFO'])
        for route in self.ordered_routes:
            if route.match(environ, start_response):
                return route.application(environ, start_response)
        logging.info("Unmatched: '%s'", environ['PATH_INFO'])

    @classmethod
    def split_args(cls, route_args):
        """
        Expects a sequence of PATH=URL routes, e.g.
            "/meals-api/=http://mac-georger.corp.cozi.com:8082/"
        """
        return [tuple(r.split('=')) for r in route_args]


def parse_args():
    parser = argparse.ArgumentParser(description='ProxyPass')
    parser.add_argument('-U', '--url',
                        help='url for the proxy')
    parser.add_argument('routes', nargs='+',
                        help='One or more PATH=URL routes')
    return parser.parse_args()

def proxy_server(ordered_routes, preproxy_url):
    """
    Runs a proxy server for a sequence of routes. Kill with Ctrl+C.

    :param ordered_routes: a sequence of PATH=URL routes.

    :param preproxy_url: url to run the server on

    Assumed to be HTTP, not HTTPS.
    """
    rules = Router.split_args(ordered_routes)
    print rules
    parts = urlparse.urlsplit(preproxy_url)
    httpserver.serve(
        Router(rules, preproxy_url),
        '0.0.0.0',
        parts.port,
        use_threadpool=True)

def proximate():
    """Console entrypoint"""
    args = parse_args()
    proxy_server(args.routes, args.url)
