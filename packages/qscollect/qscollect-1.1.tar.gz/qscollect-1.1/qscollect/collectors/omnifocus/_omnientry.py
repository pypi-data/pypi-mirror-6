import datetime
from dateutil import parser as dateparse
import pytz
from qscollect.collectors.omnifocus.helpers import _NS

EPOCH_START = datetime.datetime(1970, 1, 1)


class _OmniEntry(object):
    _DATE_FIELDS = ( "added", "modified" )
    _BOOLEAN_FIELDS = ( )
    _INTEGER_FIELDS = ( "rank" )

    @classmethod
    def _idref(cls, tag_name, value):
        return "#{0}//{1}".format(tag_name, value.attrib['idref'])

    @classmethod
    def _project(cls, reference_type, value):
        last_review = cls._date(value.find(_NS("last-review")).text)
        return _OmniEntry(last_review=last_review, is_project=True)

    _SPECIAL_FIELDS = {
        "context": "_idref",
        "task": "_idref",
        "project": "_project",
    }

    def _parse_data(self, kargs):
        values = {}
        for (key, value) in kargs.items():
            if key in self._DATE_FIELDS:
                values[key] = self._date(value.text)
            elif key in self._BOOLEAN_FIELDS:
                values[key] = self._bool(value.text)
            elif key in self._INTEGER_FIELDS:
                values[key] = self._int(value.text)
            elif key in self._SPECIAL_FIELDS:
                func = getattr(self, self._SPECIAL_FIELDS[key])
                values[key] = func(key, value)
            elif hasattr(value, "text"):
                values[key] = value.text
            else:
                values[key] = value
        return values

    def __init__(self, **kargs):
        values = self._parse_data(kargs)
        self.__dict__.update(values)

    def update(self, data):
        values = self._parse_data(data)
        self.__dict__.update(values)

    def __repr__(self):
        return "<OmniEntry: {0}>".format(str(self.__dict__))

    def to_db(self):
        data = dict(self.__dict__)
        for k, v in data.items():
            if hasattr(v, "to_db"):
                data[k] = v.to_db()

        return data

    @classmethod
    def _date(cls, value):
        return dateparse.parse(value)

    @classmethod
    def _bool(cls, value):
        return bool(value)

    @classmethod
    def _int(cls, value):
        return int(value)

    def _are_equal(self, left, right):
        if isinstance(left, datetime.datetime):
            left = left.replace(tzinfo=pytz.utc)
        if isinstance(right, datetime.datetime):
            right = right.replace(tzinfo=pytz.utc)

        return left == right

    def __eq__(self, other):
        other_dict = getattr(other, "__dict__", other)
        if len(self.__dict__) != len(other_dict):
            return False

        my_keys = sorted(self.__dict__.keys())
        other_keys = sorted(other_dict.keys())

        data = ((self.__dict__[x], other_dict[y]) for x, y in zip(my_keys, other_keys))

        return all(
            (self._are_equal(x, y) for x, y in data)
        )

    def __ne__(self, other):
        return not (self == other)
