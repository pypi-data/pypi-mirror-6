import json
import tarfile
import msgpack

from cocaine import concurrent
from cocaine.concurrent import return_
from cocaine.tools import log

__author__ = 'Evgeny Safronov <division494@gmail.com>'


def isJsonValid(text):
    try:
        json.loads(text)
        return True
    except ValueError:
        return False


def readArchive(filename):
    if not tarfile.is_tarfile(filename):
        raise tarfile.TarError('File "{0}" is not tar file'.format(filename))
    with open(filename, 'rb') as archive:
        return archive.read()


class CocaineConfigReader:
    @classmethod
    def load(cls, context, validate=lambda ctx: None):
        if isinstance(context, dict):
            log.debug('Content specified directly by dict')
            validate(context)
            return msgpack.dumps(context)

        if isJsonValid(context):
            log.debug('Content specified directly by string')
            content = context
        else:
            log.debug('Loading content from file ...')
            with open(context, 'rb') as fh:
                content = fh.read()
        content = json.loads(content)
        validate(content)
        return msgpack.dumps(content)


class Storage(object):
    def __init__(self, storage):
        self.storage = storage

    def execute(self):
        raise NotImplementedError()


class List(Storage):
    """
    Abstract storage action class which main aim is to provide find list action on 'key' and 'tags'.
    For example if key='manifests' and tags=('apps',) this class will try to find applications list
    """
    def __init__(self, key, tags, storage):
        super(List, self).__init__(storage)
        self.key = key
        self.tags = tags

    def execute(self):
        return self.storage.find(self.key, self.tags)


class Specific(Storage):
    def __init__(self, storage, entity, name):
        super(Specific, self).__init__(storage)
        self.name = name
        if not self.name:
            raise ValueError('Please specify {0} name'.format(entity))


class View(Specific):
    def __init__(self, storage, entity, name, collection):
        super(View, self).__init__(storage, entity, name)
        self.collection = collection

    @concurrent.engine
    def execute(self):
        value = yield self.storage.read(self.collection, self.name)
        return_(msgpack.loads(value))