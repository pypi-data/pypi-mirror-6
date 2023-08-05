import qscollect.db as qsdb
import qscollect.collector_base as base

ids_to_clean = []

def _setup():
    global ids_to_clean
    ids_to_clean = []

def _teardown():
    global ids_to_clean
    x = qsdb.db().keys

    for id in ids_to_clean:
        x.remove(id)

def test_collector_base_constructor():
    global ids_to_clean
    db = qsdb.db()
    ids_to_clean.append(db.keys.insert({
        "provider": "oauth",
        "name": "test",
        "apikey": "1234",
        "secret": "1234"
    }))
    x = base.CollectorBase(None, "oauth", "test")
    assert x._db is not None
    assert x.keys is not None
    assert "apikey" in x.keys
    assert "secret" in x.keys