import msgpack

from cocaine import concurrent
from cocaine.tools import actions
from cocaine.tools.actions import CocaineConfigReader
from cocaine.tools.tags import GROUPS_TAGS

__author__ = 'EvgenySafronov <division494@gmail.com>'

GROUP_COLLECTION = 'groups'


class List(actions.List):
    def __init__(self, storage):
        super(List, self).__init__(GROUP_COLLECTION, GROUPS_TAGS, storage)


class View(actions.View):
    def __init__(self, storage, name):
        super(View, self).__init__(storage, GROUP_COLLECTION, name, 'groups')


class Create(actions.Specific):
    def __init__(self, storage, name, content=None):
        super(Create, self).__init__(storage, 'group', name)
        self.content = content

    @concurrent.engine
    def execute(self):
        if self.content:
            content = CocaineConfigReader.load(self.content, validate=self._validate)
        else:
            content = msgpack.dumps({})
        yield self.storage.write(GROUP_COLLECTION, self.name, content, GROUPS_TAGS)

    def _validate(self, content):
        for app, weight in content.items():
            if not isinstance(weight, (int, long)):
                raise ValueError('all weights must be integer')


class Remove(actions.Specific):
    def __init__(self, storage, name):
        super(Remove, self).__init__(storage, 'group', name)

    def execute(self):
        return self.storage.remove(GROUP_COLLECTION, self.name)


class Refresh(actions.Storage):
    def __init__(self, locator, storage, name):
        super(Refresh, self).__init__(storage)
        self.locator = locator
        self.name = name

    @concurrent.engine
    def execute(self):
        names = yield List(self.storage).execute() if not self.name else [self.name]
        for name in names:
            yield self.locator.refresh(name)


class AddApplication(actions.Specific):
    def __init__(self, storage, name, app, weight):
        super(AddApplication, self).__init__(storage, 'group', name)
        self.app = app
        self.weight = int(weight)

    @concurrent.engine
    def execute(self):
        group = yield self.storage.read(GROUP_COLLECTION, self.name)
        group = msgpack.loads(group)
        group[self.app] = self.weight
        yield self.storage.write(GROUP_COLLECTION, self.name, msgpack.dumps(group), GROUPS_TAGS)


class RemoveApplication(actions.Specific):
    def __init__(self, storage, name, app):
        super(RemoveApplication, self).__init__(storage, 'group', name)
        self.app = app

    @concurrent.engine
    def execute(self):
        group = yield self.storage.read(GROUP_COLLECTION, self.name)
        group = msgpack.loads(group)
        if self.app in group:
            del group[self.app]
        yield self.storage.write(GROUP_COLLECTION, self.name, msgpack.dumps(group), GROUPS_TAGS)
