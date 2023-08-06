import contextlib
import logging

from sqlalchemy.engine import create_engine
from sqlalchemy.engine.url import make_url, URL
from sqlalchemy.orm.session import sessionmaker

from tangled.settings import parse_settings


log = logging.getLogger(__name__)


def include(app):
    conversion_map = {
        'url': make_url,
        'make_engine': 'object',
        'make_session_factory': 'object',
        'sessionmaker.class_': 'object',
        'sessionmaker.autoflush': 'bool',
        'sessionmaker.autocommit': 'bool',
        'sessionmaker.expire_on_commit': 'bool',
    }
    defaults = {
        'make_engine': make_engine,
        'make_session_factory': make_session_factory,
    }
    settings = parse_settings(
        app.settings, conversion_map=conversion_map, defaults=defaults,
        prefix='sqlalchemy.')

    engine = settings['make_engine'](app, settings)
    app['sqlalchemy.engine'] = engine

    session_factory = settings['make_session_factory'](app, settings)
    app['sqlalchemy.session_factory'] = session_factory

    def make_db_session(request):
        return request.app['sqlalchemy.session_factory']()

    def db_session(request):
        session = request.make_db_session()
        request.on_finished(close, session)
        return session

    def close(app, request, response, session):
        if response is None or (400 <= response.status_int < 599):
            session.rollback()
            log.debug('Session rolled back')
        else:
            session.commit()
            log.debug('Session committed')
        session.close()
        log.debug('Session closed')

    @property
    @contextlib.contextmanager
    def managed_db_session(request):
        session = request.make_db_session()
        try:
            yield session
        except:
            session.rollback()
            raise
        else:
            session.commit()
        finally:
            session.close()

    app.add_request_attribute(make_db_session)
    app.add_request_attribute(db_session, reify=True)
    app.add_request_attribute(managed_db_session)


def make_engine(app, settings):
    url = settings.get('url')
    url_args = app.get_settings(settings, 'url.')
    if url:
        for k, v in url_args.items():
            setattr(url, k, v)
    else:
        url = URL(**url_args)
    engine_args = app.get_settings(settings, 'engine.')
    engine = create_engine(url, **engine_args)
    return engine


def make_session_factory(app, settings):
    engine = app['sqlalchemy.engine']
    sessionmaker_args = app.get_settings(settings, 'sessionmaker.')
    session_factory = sessionmaker(engine, **sessionmaker_args)
    return session_factory
