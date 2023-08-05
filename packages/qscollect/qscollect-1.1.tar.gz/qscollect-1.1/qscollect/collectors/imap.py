import imaplib
import datetime
import logging
import pytz

log = logging.getLogger("IMAPCollector")

import qscollect.collector_base as collector_base


class IMAPCollector(collector_base.CollectorBase):
    """ Collects the total and the unread counts for your inbox on an imap server """
    def __init__(self, db=None):
        super(IMAPCollector, self).__init__(db, "file", "imap")

    def register(self, system):
        self._system = system
        system.register_schedule(self, hour=1)

    def __call__(self, config=None):
        if config is None:
            config = self.keys

        logging.debug(config)
        port = int(config['port'])

        if config['ssl']:
            imap = imaplib.IMAP4_SSL(config['server'], port)
        else:
            imap = imaplib.IMAP4(config['server'], port)

        password = open(config['password_path'], "r").readline().strip()

        imap.login(config['username'], password)
        total_count = int(imap.select(readonly=True)[1][0])
        unread_count = len(imap.search(None, 'UnSeen')[1][0].split())
        todo_count = int(imap.select('2do', readonly=True)[1][0])
        modified = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
        log.debug("{0} {1}/{2}-{3}".format(modified, unread_count, total_count, todo_count))

        yield {
            'modified': modified,
            'total': total_count,
            'unread': unread_count,
            'todo': todo_count
        }
