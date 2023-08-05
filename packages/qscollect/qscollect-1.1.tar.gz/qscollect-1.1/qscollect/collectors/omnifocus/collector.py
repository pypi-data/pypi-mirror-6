import logging
from os import path as path
import os
from qscollect import collector_base as base


class _PreviousState(object):
    def __init__(self, dict_):
        if dict_ is None:
            dict_ = {}
        self.tasks = dict_.get("tasks", {})
        self.contexts = dict_.get("context", {})
        self._id = dict_.get("_id", "")


class OmniFocusCollector(base.CollectorBase):
    def __init__(self, db=None):
        super(OmniFocusCollector, self).__init__(db, "file", "omnifocus")

    def register(self, system):
        self._system = system
        system.register_schedule(self, minute=30)

    def __call__(self, ofocus_file=None, previous_state=None):
        if ofocus_file is None:
            ofocus_file = self.keys["ofocus_file"]
        if previous_state is None:
            previous_state = _PreviousState(self._db.get("omnifocus_data", {"object_type": "previous_state"}))

        import qscollect.collectors.omnifocus._omnifocus as omnifocus
        import qscollect.collectors.omnifocus._omnidelta as delta

        zip_paths = (path.join(ofocus_file, x) for x in sorted(os.listdir(ofocus_file)) if x.endswith(".zip"))
        omni = omnifocus.OmniFocus()
        for zip_path in zip_paths:
            omni.feed(zip_path)

        diff = delta.OmniDelta(previous_state, omni)
        for change in diff.delta:
            yield change

        logging.info("Saving Previous State")

        state = omni.state

        yield {
            "tasks": dict(((k, v.to_db()) for k,v in state['tasks'].items())),
            "contexts": dict(((k, v.to_db()) for k,v in state['contexts'].items())),
            "_id": previous_state._id,
            "object_type": "previous_state"
        }