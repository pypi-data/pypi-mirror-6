import qscollect.collectors.imap as imap
import os.path as path

IMAP_CONFIG = {
    "ssl": True,
    "server": 'imap.gmail.com',
    "port": '993',
    "password_path": path.expanduser('~/.imap_passwd'),
    "username": 'russell.hay@gmail.com',
}

def test_imap_collector():
    x = imap.IMAPCollector("foo")
    y = list(x(IMAP_CONFIG))

    assert len(y) == 1
    assert 'total' in y[0]
    assert 'unread' in y[0]
    assert 'modified' in y[0]
    assert y[0]['total'] > 0
    assert y[0]['unread'] > 0
    assert y[0]['todo'] > 0