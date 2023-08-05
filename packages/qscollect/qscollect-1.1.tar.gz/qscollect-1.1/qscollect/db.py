import logging
import pymongo as mongo

class ConnectionNotEstablished(Exception): pass

class db(object):
    CONNECTION = ('localhost', 27017)
    DATABASE = 'qs'

    def __init__(self, client=None):
        self._client = client

    @property
    def client(self):
        if self._client is None:
            self._client = mongo.MongoClient(*(self.CONNECTION))

        return self._client

    def record(self, name, row):
        self._save("{0}_data".format(name), row)

    @property
    def database(self):
        return self.client[self.DATABASE]

    def collection(self, name):
        return self.database[name]

    def get(self, collection, dict_):
        return self.collection(collection).find_one(dict_)

    @property
    def keys(self):
        return self.collection('keys')

    @property
    def state(self):
        return self.collection('state')

    def set_config(self, name, provider, data):
        row = dict(data)
        row['name'] = name
        row['provider'] = provider

        self._save("keys", row)

    def set_state(self, name, data):
        row = dict(data)
        row['collector'] = name

        row = self._expand_row(row)
        if row is None:
            return

        data = self.get_state(name)
        if data is None:
            data = { }
        for k,v in row.items():
            if not k.startswith('_'):
                data[k] = v

        self._save("state", data)

    def get_state(self, name):
        retval = self.state.find_one({
            "collector": name
        })

        return retval

    def _expand_row(self, row):
        if hasattr(row, "to_db"):
            row = row.to_db()
        return row

    def _save(self, name, row):
        row = self._expand_row(row)
        if row is None:
            return

        collection = self.collection(name)
        collection.save(row)
