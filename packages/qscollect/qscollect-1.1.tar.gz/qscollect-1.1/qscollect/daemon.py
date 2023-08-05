import datetime
import time
import itertools
import logging
import qscollect.db as qsdb
import Queue


def factory(config, collectors, daemonize=True):
    retval = QSCollect(config, collectors)
    if daemonize:
        retval = Daemon(retval)  # Daemonize it

    return retval

class QSCollect(object):
    def __init__(self, config, collectors, db=None):
        if db is None:
            self._db = qsdb.db()
        else:
            self._db = db
        self._config = config
        self._collectors = [x(self._db) for x in collectors]
        self._request_queue = Queue.Queue()
        self._schedule = {}
        self._scheduled_updates = []

    @property
    def tick_interval(self):
        return self._config.get("main", {}).get("tick", 1)

    def run(self):
        # Register all of the collectors
        map(lambda x: x.register(self), self._collectors)

        while True:
            try:
                iterator = self._request_queue.get(block=False)
                name = iterator.name
                rows = list(iterator())
                [self._db.record(name, x) for x in rows if x is not None]
            except Queue.Empty:
                self._process_scheduled_requests()
                time.sleep(self.tick_interval)


    def register_schedule(self, collector, day=0, hour=0, minute=0):
        self._schedule[collector] = (day, hour, minute)
        self._scheduled_updates.append((datetime.datetime.min, collector))  # schedule an immediate update

    def schedule(self, iterator):
        self._request_queue.queue(iterator)

    def _process_scheduled_requests(self):
        ready_schedules = itertools.ifilter(lambda x: x[0] < datetime.datetime.now(), self._scheduled_updates)
        for ready in ready_schedules:
            logging.info("Running Scheduled Update: {0}".format(type(ready[1]).__name__))
            self._scheduled_updates.remove(ready)
            self._request_queue.put(ready[1])

            interval = self._schedule[ready[1]]
            next_update = datetime.datetime.now() + datetime.timedelta(days=interval[0],
                                                                       hours=interval[1],
                                                                       minutes=interval[2])
            self._scheduled_updates.append((next_update, ready[1]))  # schedule next update


class Daemon(object):
    def __init__(self, parent):
        self._parent = parent

    def run(self):
        pass