import threading
import logging
from tg import config

transaction = None

def configure_transaction():
    global transaction
    try:
        import transaction
    except ImportError: #pragma: no cover
        class FakeTransaction(object):
            def noop(*args):
                pass
            begin = abort = commit = noop
        class MingTransaction(FakeTransaction):
            def commit(self):
                config.DBSession.flush()
            def abort(self):
                config.DBSession.clear()
        transaction = MingTransaction() if getattr(config, 'use_ming', False) else FakeTransaction()

def remove_session(session):
    if getattr(config, 'use_sqlalchemy', False):
        return session.remove()
    return session.clear_all()

log = logging.getLogger('tgext.asyncjob')

running_status = threading.local()

class AsyncWorkerThread(threading.Thread):
    def __init__(self, queue):
        super(AsyncWorkerThread, self).__init__()
        self.queue = queue

    def run(self):
        log.info('Worker thread is running.')

        if transaction is None:
            configure_transaction()

        while True:
            msg = self.queue.get()

            func = msg.get('callable')
            args = msg.get('args')
            params = msg.get('params')
            uid = msg.get('uid')

            if not args:
                args = []

            if not params:
                params = {}

            if func:
                transaction.begin()
                try:
                    running_status.entry = uid
                    func(*args, **params)
                    transaction.commit()
                except Exception:
                    log.exception('Exception in async job %s', uid)
                    transaction.abort()

            running_status.entry = None
            self.queue.done(uid)

            try:
                remove_session(config.DBSession)
            except AttributeError:
                pass

def asyncjob_running_uid():
    return running_status.entry

