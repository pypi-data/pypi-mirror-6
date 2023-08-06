import logging
import os

from beaker.session import SessionObject

from tangled.converters import as_first_of
from tangled.decorators import reify
from tangled.settings import parse_settings

from .flash import FlashFactory


log = logging.getLogger(__name__)


def include(app):
    conversion_map = {
        'auto': 'bool',
        # TODO: Support datetime and timedelta too?
        'cookie_expires': as_first_of('int', 'bool'),
    }
    defaults = {
        'auto': True,
        'cookie_expires': True,
        'type': 'file',
        'data_dir': os.path.join(os.getcwd(), 'data/session'),
    }
    required = ('key', 'secret')
    settings = parse_settings(
        app.settings, conversion_map=conversion_map, defaults=defaults,
        required=required, prefix='beaker.session.')
    app['session_factory'] = SessionObject
    app['session_factory.args'] = settings
    app.add_request_attribute(session)
    app.add_request_attribute(flash)


@reify
def session(request):
    app = request.app
    factory = app['session_factory']
    args = app['session_factory.args']
    sess = factory(request.environ, **args)
    request.on_finished(persist, sess)
    return sess


@reify
def flash(request):
    return FlashFactory(request.app, request, request.session)


def persist(app, request, response, sess):
    if response and response.status_code < 400 and sess.accessed():
        sess.persist()
        log.debug('Session persisted')
        sess_headers = sess.__dict__['_headers']
        if sess_headers['set_cookie']:
            cookie = sess_headers['cookie_out']
            if cookie:
                response.headerlist.append(('Set-cookie', cookie))
                log.debug('Session cookie set to: {}'.format(cookie))
