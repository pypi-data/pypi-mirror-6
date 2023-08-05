import qscollect.collectors.omnifocus._omnientry
import qscollect.collectors.omnifocus._omnifocus as omnifocus
import qscollect.collectors.omnifocus._omnidelta as omnidelta
import helpers as h

MAIN_FILE = h.data_file("OmniFocus.ofocus", "00000000000000=kV9d0GF_JyT+goN-Zro_PV9.zip")
TRANSACTION_FILE = h.data_file("OmniFocus.ofocus", "20130823050312=goN-Zro_PV9+mLDqVX6bL-E.zip")


def test_checkpoint_snapshot_parsing():
    x = omnifocus.OmniFocus()
    assert x is not None
    x.feed(MAIN_FILE)

    assert x.tasks is not None
    assert len(x.tasks) > 0


def test_transactional_new_task():
    x = omnifocus.OmniFocus()
    x.feed(MAIN_FILE)
    task_count = len(x.tasks)

    x.feed(TRANSACTION_FILE)
    new_task_count = len(x.tasks)

    assert task_count + 1 == new_task_count, "Transactional file did not add a new task"


def test_transactional_update_task():
    x = omnifocus.OmniFocus()
    x.feed(MAIN_FILE)
    first_modified_date = x.tasks["j8_jxU9x4nN"].modified

    x.feed(TRANSACTION_FILE)
    second_modified_date = x.tasks["j8_jxU9x4nN"].modified

    assert first_modified_date != second_modified_date


def test_entry_equality():
    x = qscollect.collectors.omnifocus._omnientry._OmniEntry(x=1, y=2)
    y = qscollect.collectors.omnifocus._omnientry._OmniEntry(x=1, y=2)

    assert x == y


def test_entry_inequality():
    x = qscollect.collectors.omnifocus._omnientry._OmniEntry(x=1, y=1)
    y = qscollect.collectors.omnifocus._omnientry._OmniEntry(x=1, y=2)

    assert x != y


def test_delta():
    x = omnifocus.OmniFocus()
    x.feed(MAIN_FILE)

    y = omnifocus.OmniFocus()
    y.feed(MAIN_FILE)
    y.feed(TRANSACTION_FILE)

    delta = omnidelta.OmniDelta(x, y)

    assert len(delta._context_changes) == 0
    assert len(delta._task_changes) == 3

    all_deltas = delta.to_json()
    print all_deltas
    assert all_deltas == '[{"added": "2013-08-23 05:03:12.449000+00:00", "entry_type": "task", "delta_type": "add", "object_id": "j58Dbbl8Xk4", "task": "#task//j8_jxU9x4nN", "rank": -1073741824, "context": "#context//mi4x2-Wc8nd", "order": "parallel"}, null, null]'