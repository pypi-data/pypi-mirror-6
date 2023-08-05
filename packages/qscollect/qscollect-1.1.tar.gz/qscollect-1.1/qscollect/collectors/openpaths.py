import qscollect.collector_base as base

class OpenPathsCollector(base.CollectorBase):
    def __init__(self, db=None):
        super(OpenPathsCollector, self).__init__(db, "oauth", "openpaths")