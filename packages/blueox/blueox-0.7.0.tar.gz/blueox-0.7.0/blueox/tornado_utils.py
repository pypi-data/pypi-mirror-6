# -*- coding: utf-8 -*-

"""
blueox.tornado
~~~~~~~~

This module provides hooks for using blueox with the Tornado async web server.
Making blueox useful inside tornado is a challenge since you'll likely want a
blueox context per request, but multiple requests can be going on at once inside
tornado.

:copyright: (c) 2012 by Rhett Garber
:license: ISC, see LICENSE for more details.

"""
import functools
import logging
import traceback
import types

log = logging.getLogger(__name__)

import tornado.web
import tornado.gen
import tornado.simple_httpclient
import tornado.stack_context

import blueox


def _gen_wrapper(ctx, generator):
    """Generator Wrapper that starts/stops our context
    """
    while True:
        ctx.start()

        try:
            v = generator.next()
        except (tornado.gen.Return, StopIteration):
            ctx.done()
            raise
        else:
            ctx.stop()
            yield v


def coroutine(func):
    """Replacement for tornado.gen.coroutine that manages a blueox context

    The difficulty with managing global blueox contexts in an async environment
    is contexts will need to start and stop depending on what steps of a
    coroutine are running. This decorator wraps the default coroutine decorator
    allowing us to stop and restore the context whenever this coroutine runs.

    If you don't use this wrapper, unrelated contexts may be grouped together!
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            ctx = args[0].blueox_ctx
        except (AttributeError, IndexError):
            ctx = None

        # Remember, not every coroutine wrapped method will return a generator,
        # so we have to manage context switching in multiple places.
        if ctx is not None:
            ctx.start()

        result = func(*args, **kwargs)

        if ctx is not None:
            ctx.stop()

        if isinstance(result, types.GeneratorType):
            return _gen_wrapper(ctx, result)

        return result

    real_coroutine = tornado.gen.coroutine
    return real_coroutine(wrapper)


class BlueOxRequestHandlerMixin(object):
    """Include in a RequestHandler to get a blueox context for each request

    """
    blueox_name = "request"

    def prepare(self):
        self.blueox_ctx = blueox.Context(self.blueox_name)
        self.blueox_ctx.start()
        super(BlueOxRequestHandlerMixin, self).prepare()

    def on_finish(self):
        super(BlueOxRequestHandlerMixin, self).on_finish()
        self.blueox_ctx.done()
        self.blueox_ctx = None


class SampleRequestHandler(BlueOxRequestHandlerMixin, tornado.web.RequestHandler):
    """Sample base request handler that provides basic information about the request.
    """
    def prepare(self):
        super(SampleRequestHandler, self).prepare()
        blueox.set('headers', self.request.headers)
        blueox.set('method', self.request.method)
        blueox.set('uri', self.request.uri)

    def write_error(self, status_code, **kwargs):
        if 'exc_info' in kwargs:
            blueox.set('exception', ''.join(traceback.format_exception(*kwargs["exc_info"])))

        return super(SampleRequestHandler, self).write_error(status_code, **kwargs)

    def write(self, chunk):
        blueox.add('response_size', len(chunk))
        return super(SampleRequestHandler, self).write(chunk)

    def on_finish(self):
        blueox.set('response_status_code', self._status_code)
        super(SampleRequestHandler, self).on_finish()


class AsyncHTTPClient(tornado.simple_httpclient.SimpleAsyncHTTPClient):
    def __init__(self, *args, **kwargs):
        self.blueox_name = '.httpclient'
        return super(AsyncHTTPClient, self).__init__(*args, **kwargs)

    def fetch(self, request, callback=None, **kwargs):
        ctx = blueox.Context(self.blueox_name)
        ctx.start()
        if isinstance(request, basestring):
            ctx.set('request.uri', request)
            ctx.set('request.method', kwargs.get('method', 'GET'))
        else:
            ctx.set('request.uri', request.url)
            ctx.set('request.method', request.method)
            ctx.set('request.size', len(request.body) if request.body else 0)

        ctx.stop()

        # I'd love to use the future to handle the completion step, BUT, we
        # need this to happen first. If the caller has provided a callback, we don't want them
        # to get called before we do. Rather than poke into the internal datastructures, we'll just 
        # handle the callback explicitly

        def complete_context(response):
            ctx.start()

            ctx.set('response.code', response.code)
            ctx.set('response.size', len(response.body) if response.body else 0)

            ctx.done()

        if callback is None:
            def fetch_complete(future):
                complete_context(future.result())

            future = super(AsyncHTTPClient, self).fetch(request, **kwargs)
            future.add_done_callback(fetch_complete)
        else:
            def callback_wrapper(response):
                complete_context(response)
                callback(response)

            future = super(AsyncHTTPClient, self).fetch(request, callback=callback_wrapper, **kwargs)

        return future
