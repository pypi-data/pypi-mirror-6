import qscollect.db as qsdb

TEST_COLLECTION = 'openpaths'

def _cleanup_collection():
    x = qsdb.db().database
    x.drop_collection(TEST_COLLECTION)

def test_db_connection():
    x = qsdb.db()
    assert x is not None
    assert x.client is not None
    assert x.database is not None
    assert x.collection(TEST_COLLECTION) is not None

def test_insert():
    x = qsdb.db()
    y = x.collection(TEST_COLLECTION)
    id = y.insert({'Foo': 'Bar'})
    assert id is not None

    doc = y.find_one(id)
    assert 'Foo' in doc
    assert doc['Foo'] == 'Bar'
test_insert.teardown = _cleanup_collection