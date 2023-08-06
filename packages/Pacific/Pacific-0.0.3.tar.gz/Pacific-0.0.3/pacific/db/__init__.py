"""
This package provides an API for relational databases.
"""
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker

from pacific.db.repository import repository_config
from pacific.db.repository import add_repository


__all__ = ['repository_config', 'get_session_factories']


def includeme(config):
    """ Pyramid configuration entry point.
    Call me before using any of the SQL Sessions.

    :param config: Pyramid configurator instance
    :type config: :class:`pyramid.config.Configurator`
    """
    config.registry.settings['pacific.db.session_factories'] = get_session_factories(config.registry.settings)

    config.add_request_method(request_db, 'db', reify=True)
    # Add a directive that is capable of registering project repositories
    config.add_directive('add_repository', add_repository)


def get_session_factories(settings, options_prefix='pacific.db.'):
    """

    :param settings:
    :type settings: dict
    :param options_prefix:
    :type options_prefix: str
    :return: dict of {domain => {shard => sessionmaker()}} session factories
    :rtype: dict
    """
    session_factories = {}
    for key, value in settings.items():
        if not key.startswith(options_prefix):
            continue

        key = key.split(options_prefix)[1]
        domain, shard = key.split('.')
        url = value
        engine = sa.create_engine(url, encoding='utf-8',
                                  # -- pool options --
                                  pool_size=10,
                                  max_overflow=10,
                                  pool_timeout=10)
        shard_sessions = session_factories.setdefault(domain, {})
        shard_sessions[shard] = sessionmaker(bind=engine, autocommit=False)
    return session_factories


def request_db(request):
    """

    :param request: Pyramid Request instance
    :type request: :class:`pyramid.request.Request`
    :return: an instance of :class:`RequestDbApi`
    :rtype: :class:`pacific.db.RequestDbApi`
    """
    request.add_finished_callback(lambda request: request.db.discard())
    return RequestDbApi(request)


class RequestDbApi(object):
    """ An instance of this class is used as ``request.db`` attribute.
    """
    def __init__(self, request):
        """
        :param request: Pyramid Request instance
        :type request: :class:`pyramid.request.Request`
        """
        registry_settings = request.registry.settings
        self.repositories = registry_settings['pacific.db.repositories']
        self.session_factories = registry_settings['pacific.db.session_factories']

        self.sessions = {}
        self.repository_instances = {}


    def get_repository(self, name):
        """ Returns an instance of a Repository object.

        :param name: repository name
        :type name: str
        :return: repository instance
        """
        try:
            repository_instance = self.repository_instances[name]
        except KeyError:
            repository_conf = self.repositories[name]
            session_instance = self.get_session(repository_conf['namespace'], repository_conf['shard'])
            repository_instance = repository_conf['repository'](session_instance)
            self.repository_instances[name] = repository_instance
        return repository_instance

    def get_session(self, namespace, shard='default'):
        """ Returns a SQLAlchemy Session instance according to the given namespace and shard.

        :param namespace: namespace name according to Pacific config.
        :type namespace: str
        :param shard: one of the namespace shards. Shard 'default' is required to be set up
                      in the config.
        :type shard: str
        :return: SQLAlchemy's Session instance.
        :rtype: :class:`sqlalchemy.orm.session.Session`
        """
        key = '{namespace}:{shard}'.format(namespace=namespace, shard=shard)
        try:
            # find existing session instance
            session_instance = self.sessions[key]
        except KeyError:
            # start a new session
            session_instance = self.session_factories[namespace][shard]()
            self.sessions[key] = session_instance
        return session_instance

    def discard(self):
        """Close all sessions and return connections to the pool."""
        for sess in self.sessions.values():
            sess.close()
