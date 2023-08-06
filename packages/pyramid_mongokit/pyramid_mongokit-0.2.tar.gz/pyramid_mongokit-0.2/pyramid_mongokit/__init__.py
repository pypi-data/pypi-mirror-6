import os
import logging
import urlparse


import mongokit
import venusian

from pymongo import ReadPreference
from pymongo.uri_parser import parse_uri

from pyramid.decorator import reify

from zope.interface import Interface, implementer

log = logging.getLogger(__name__)

__all__ = ['register_document', 'generate_index', 'get_mongo_connection']


def includeme(config):
    log.info('Configure mongokit connection...')
    db_prefix = os.environ.get('MONGO_DB_PREFIX', '')

    mongo_uri = os.environ['MONGO_URI']
    res = parse_uri(mongo_uri)

    params = {
        'auto_start_request': False,
        'tz_aware': True,
        'read_preference': ReadPreference.SECONDARY_PREFERRED,
        }

    # Udpate params with options contained in uri in order to ensure their
    # use for mongo_client initialization
    params.update(res['options'])

    if 'MONGO_DB_NAME' in os.environ:
        if 'replicaset' in params:
            cls = ReplicasetSingleDbConnection
        else:
            cls = SingleDbConnection

        connection = cls(
            os.environ['MONGO_DB_NAME'],
            db_prefix,
            mongo_uri,
            **params)

        config.add_request_method(mongo_db, 'mongo_db', reify=True)
    else:
        if 'replicaset' in params:
            cls = ReplicasetMongoConnection
        else:
            cls = MongoConnection
        connection = cls(
            db_prefix,
            mongo_uri,
            **params)
        config.add_request_method(mongo_db, 'get_mongo_db')

    config.registry.registerUtility(connection, name='mongo_connection')

    config.add_request_method(mongo_connection, 'mongo_connection',
                              reify=True)
    config.add_directive('register_document', directive_register_document)
    config.add_directive('generate_index', directive_generate_index)
    config.add_directive('get_mongo_connection', directive_mongo_connection,
                         action_wrap=False)

    log.info('Mongo connection configured...')


class IMongoConnection(Interface):
    pass


class MongoConnectionMixin(object):

    def __init__(self, db_prefix, *args, **kwargs):
        self.db_prefix = db_prefix

    def get_db(self, db_name):
        return getattr(self, '%s%s' % (self.db_prefix, db_name))

    def generate_index(self, document_cls, db_name=None, collection=None):
        collection = collection if collection else document_cls.__collection__
        document_cls.generate_index(self.get_db(db_name)[collection])

    def prefixed_database_names(self):
        return (name for name in self.database_names()
                if name.startswith(self.db_prefix))


def get_uri_with_db_name(uri, db_prefix, db_name):
        res = list(urlparse.urlsplit(uri))
        res[2] = db_prefix + db_name
        return urlparse.urlunsplit(res)


class SingleDbConnectionMixin(MongoConnectionMixin):

    def __init__(self, db_prefix, db_name, *args, **kwargs):
        super(SingleDbConnectionMixin, self).__init__(db_prefix, *args,
                                                      **kwargs)
        self.db_name = db_name

    @reify
    def db(self):
        return self.get_db(self.db_name)

    def get_db(self, db_name=None):
        return super(SingleDbConnectionMixin, self).get_db(self.db_name)

    def generate_index(self, document_cls, db_name=None, collection=None):
        super(SingleDbConnectionMixin, self).generate_index(document_cls,
                                                            self.db_name,
                                                            collection)


@implementer(IMongoConnection)
class MongoConnection(mongokit.Connection, MongoConnectionMixin):
    def __init__(self, db_prefix, *args, **kwargs):
        log.info('Creating SingleDbConnection: args=%s kwargs=%s',
                 args, kwargs)
        MongoConnectionMixin.__init__(self, db_prefix, *args, **kwargs)
        mongokit.Connection.__init__(self, *args, **kwargs)


@implementer(IMongoConnection)
class SingleDbConnection(mongokit.Connection, SingleDbConnectionMixin):
    def __init__(self, db_name, db_prefix, uri, *args, **kwargs):
        log.info('Creating SingleDbConnection: args=%s kwargs=%s',
                 args, kwargs)

        uri = get_uri_with_db_name(uri, db_prefix, db_name)
        SingleDbConnectionMixin.__init__(self, db_name, db_prefix, *args,
                                         **kwargs)

        mongokit.Connection.__init__(self, uri, *args, **kwargs)


@implementer(IMongoConnection)
class ReplicasetMongoConnection(mongokit.ReplicaSetConnection,
                                MongoConnectionMixin):
    def __init__(self, db_prefix, *args, **kwargs):
        log.info('Creating ReplicasetMongoConnection: args=%s kwargs=%s',
                 args, kwargs)
        MongoConnectionMixin.__init__(self, db_prefix, *args, **kwargs)

        mongokit.ReplicaSetConnection.__init__(self, *args, **kwargs)


@implementer(IMongoConnection)
class ReplicasetSingleDbConnection(mongokit.ReplicaSetConnection,
                                   SingleDbConnectionMixin):
    def __init__(self, db_name, db_prefix, uri, *args, **kwargs):
        log.info('Creating ReplicasetSingleDbConnection: args=%s kwargs=%s',
                 args, kwargs)

        uri = get_uri_with_db_name(uri, db_prefix, db_name)

        SingleDbConnectionMixin.__init__(self, db_name, db_prefix, *args,
                                         **kwargs)

        mongokit.ReplicaSetConnection.__init__(self, uri, *args, **kwargs)


def directive_generate_index(config, document_cls, db_name='',
                             collection=None):
    db = generate_index(config.registry, document_cls, db_name, collection)
    if config.introspection:
        intr = config.introspector.get('Mongokit Documents', document_cls)
        if intr:
            intr['databases'].append(db)


def generate_index(registry, document_cls, db_name='', collection=None):
    mongo_connection = get_mongo_connection(registry)
    mongo_connection.generate_index(document_cls, db_name=db_name,
                                    collection=collection)
    return mongo_connection.get_db(db_name)


def directive_register_document(config, document_cls_or_list):
    register_document(config.registry, document_cls_or_list)

    if config.introspection:

        if not isinstance(document_cls_or_list, (list, tuple)):
            document_cls_or_list = (document_cls_or_list, )

        for document_cls in document_cls_or_list:
            intr = config.introspector.get('Mongokit Documents', document_cls)
            if not intr:
                intr = config.introspectable(
                    category_name='Mongokit Documents',
                    discriminator=document_cls,
                    title=document_cls,
                    type_name='Document',
                )
                intr['databases'] = []
                config.introspector.add(intr)
            config.action(document_cls, introspectables=(intr, ))


def register_document(registry, document_cls_or_list):
    mongo_connection = get_mongo_connection(registry)
    mongo_connection.register(document_cls_or_list)


def directive_mongo_connection(config):
    return get_mongo_connection(config.registry)


def get_mongo_connection(registry):
    return registry.getUtility(IMongoConnection, u'mongo_connection')


def mongo_connection(request):
    """This method is dedicated to be reified.
    It ensure that current thread or greenlet always use the same socket until
    request processing is over.
    """
    mongo_client = get_mongo_connection(request.registry)
    mongo_client.start_request()
    request.add_finished_callback(end_request)
    return mongo_client


def end_request(request):
    request.mongo_connection.end_request()


def mongo_db(request, db_name=False):
    conn = request.mongo_connection
    if db_name:
        return conn.get_db(db_name)
    return conn.db


class register(object):
    """Decorator to register document to mongokit while doing config.scan"""

    def __init__(self, generate_index=True, **settings):
        self.__dict__.update(settings)
        self.generate_index = generate_index

    def __call__(self, document_cls):
        settings = self.__dict__.copy()
        generate_index = settings.pop('generate_index')

        def callback(context, name, cls):
            config = context.config.with_package(info.module)
            config.register_document(cls, **settings)
            if generate_index:
                config.generate_index(cls)

        info = venusian.attach(document_cls, callback)
        settings['_info'] = info.codeinfo
        return document_cls
