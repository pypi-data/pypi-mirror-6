import logging
import jsonpickle
import qscollect.collectors.omnifocus._deltacalculator as delta


class _DeltaBase(object):
    def __init__(self, id_, entry):
        self._id = id_
        self._entry = entry

    def __setstate__(self, state):
        raise NotImplementedError

    @property
    def type_(self):
        return "base"

    def to_db(self):
        data = self.__getstate__()
        if data is None:
            return None
        for k, v in data.items():
            if hasattr(v, "to_db"):
                data[k] = v.to_db()  # In case we have embedded objects

        return data

    def __repr__(self):
        return "<{0}: {1}>".format(self.type_, str(self.to_db()))


class _DeltaUpdate(_DeltaBase):
    def __init__(self, id_, left_entry, right_entry):
        super(_DeltaUpdate, self).__init__(id_, left_entry)
        self._right = right_entry
        self._delta_data = {}
        delta_left = getattr(self._entry, "__dict__", self._entry)
        delta_right = getattr(self._right, "__dict__", self._right)
        logging.debug("DELTA {0} / {1}".format(delta_left, delta_right))
        d = delta.TreeDeltaCalculator(delta_left, delta_right, _DeltaPropertyState(), True)
        if len(d) == 1 and d.keys()[0] == "modified":
            # If it just updates the modified type and nothing else, it's just OmniFocus being overzelous, ignore.
            self._delta_data = None
        else:
            self._delta_data.update(d)

    def __getstate__(self):
        if self._delta_data is None:
            return None

        data = dict(self._delta_data)
        data["delta_type"] = "update"
        data["entry_type"] = self._entry["entry_type"]
        data["object_id"] = self._entry["object_id"]

        return data

    @property
    def type_(self):
        return "update"


class _DeltaAdd(_DeltaBase):
    def __getstate__(self):
        data = dict(self._entry.__dict__)
        data["delta_type"] = "add"

        return data

    @property
    def type_(self):
        return "add"


class _DeltaDelete(_DeltaBase):
    def __getstate__(self):
        data = dict(getattr(self._entry, "__dict__", self._entry))
        data["delta_type"] = "delete"

        return data

    @property
    def type_(self):
        return "delete"


class _DeltaPropertyState(object):
    def __init__(self):
        self._changes = {}

    @property
    def changes(self):
        return self._changes

    def update(self, id_, _, right):
        self._changes[id_] = right

    def add(self, id_, entry):
        self._changes[id_] = entry

    def delete(self, id_, _):
        self._changes[id_] = None


class _DeltaState(object):
    def __init__(self):
        self._changes = []

    @property
    def changes(self):
        return self._changes

    def update(self, id_, left, right):
        self._changes.append(_DeltaUpdate(id_, left, right))

    def add(self, id_, entry):
        self._changes.append(_DeltaAdd(id_, entry))

    def delete(self, id_, entry):
        self._changes.append(_DeltaDelete(id_, entry))


class OmniDelta(object):
    def __init__(self, left, right):
        self._left = left
        self._right = right
        self._task_changes = []
        self._context_changes = []

        self._calculate_delta()

    def _calculate_delta(self):
        self._calculate_task_delta()
        self._calculate_context_delta()

    def _calculate_task_delta(self):
        self._task_changes = delta.TreeDeltaCalculator(self._left.tasks, self._right.tasks, _DeltaState())


    def _calculate_context_delta(self):
        self._context_changes = delta.TreeDeltaCalculator(self._left.contexts, self._right.contexts, _DeltaState())

    @property
    def delta(self):
        return list(self._task_changes + self._context_changes)

    def to_json(self):
        return jsonpickle.encode(self.delta, unpicklable=False)
