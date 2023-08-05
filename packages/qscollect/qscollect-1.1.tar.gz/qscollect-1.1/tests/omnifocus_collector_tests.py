import jsonpickle
import qscollect.collectors.omnifocus as omnifocus
import qscollect.collectors.omnifocus._omnifocus as _omnifocus
import helpers as h
from qscollect.collectors.omnifocus.collector import OmniFocusCollector

DATA_FILE = h.data_file("OmniFocus.ofocus")
PREVIOUS_STATE_FILE = h.data_file("OmniFocus.ofocus", "00000000000000=kV9d0GF_JyT+goN-Zro_PV9.zip")


def test_delta_calculation():
    x = OmniFocusCollector(db="foo")
    y = _omnifocus.OmniFocus()
    y.feed(PREVIOUS_STATE_FILE)

    assert x is not None

    actual = list(x(DATA_FILE, y))
    assert len(actual) == 9
    assert len(filter(lambda x: x.type_ == 'update', actual)) == 8
    assert len(filter(lambda x: x.type_ == 'add', actual)) == 1
