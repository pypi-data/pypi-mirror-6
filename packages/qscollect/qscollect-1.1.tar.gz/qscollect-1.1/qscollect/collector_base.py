import importlib
import logging
import sys

import qscollect.db as qsdb


class CollectorBase(object):
    def __init__(self, db, provider=None, name=None):
        if db is None:
            self._db = qsdb.db()
        else:
            self._db = db
        self._keys = None
        self._state = None

        if provider is None:
            provider = self.__class__.Meta.style

        if name is None:
            name = self.__class__.Meta.name

        self._provider = provider
        self._name = name
        self._system = None

    @property
    def name(self):
        return self._name

    @property
    def keys(self):
        if self._keys is None:
            self._keys = self._db.keys.find_one({
                "provider": self._provider,
                "name": self._name
            })

        return self._keys

    @property
    def state(self):
        if self._state is None:
            self._state = self._db.get_state(self._name)

        return self._state

    def register(self, system):
        raise NotImplementedError("Collectors must implement register: {0}".format(type(self).__name__))


class Loader(object):
    def __init__(self):
        self._collectors = []

    def load(self, collector_name):
        parts = collector_name.split('.')
        modulename = ".".join(parts[:-1])
        classname = parts[-1]
        module = importlib.import_module(modulename)
        real_module = sys.modules[module.__name__]
        logging.info("Loading Collector {0}".format(module.__name__))
        self._collectors.append(getattr(real_module, classname))


    @property
    def collectors(self):
        return self._collectors