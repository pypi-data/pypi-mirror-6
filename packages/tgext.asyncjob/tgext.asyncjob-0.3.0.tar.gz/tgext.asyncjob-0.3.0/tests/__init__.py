import tg
from tgext.asyncjob import start_async_worker

class FakeAppGlobals(object):
    pass

tg.app_globals = FakeAppGlobals()

def setUp():
    start_async_worker(tg.app_globals)

