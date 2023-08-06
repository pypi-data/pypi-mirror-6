from .tghooks import start_async_worker
from .worker import asyncjob_running_uid
from .progress import asyncjob_set_progress, asyncjob_get_progress
from .queue import asyncjob_perform
from .sqlahelpers import asyncjob_timed_query
from tg.configuration import milestones

import logging
log = logging.getLogger('tgext.asyncjob')

def plugme(configurator, options=None):
    if options is None:
        options = {}

    log.info('Setting up tgext.asyncjob...')

    milestones.environment_loaded.register(lambda: start_async_worker(options.get('app_globals'),
                                                                      options.get('progress_tracker')))

    return dict(appid='tgext.asyncjob')
