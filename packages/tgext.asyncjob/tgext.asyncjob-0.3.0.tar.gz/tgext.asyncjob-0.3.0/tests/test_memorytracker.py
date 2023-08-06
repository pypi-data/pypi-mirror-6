import tg
from .utils import TestTask

from tgext.asyncjob.trackers.memory import MemoryProgressTracker
from tgext.asyncjob.progress import asyncjobs_progress_status

from tgext.asyncjob import asyncjob_perform, asyncjob_get_progress, asyncjob_set_progress

def setUp():
    asyncjobs_progress_status._tracker = MemoryProgressTracker()

class TestMemoryTracker(object):
    def setUp(self):
        self.task = TestTask()

    def tearDown(self):
        self.task.complete()

    def test_start_job(self):
        jobid = asyncjob_perform(self.task)

        self.task.wait_for_start()
        status = asyncjob_get_progress(jobid)
        assert status == (-1, None), status

    def test_job_completion(self):
        jobid = asyncjob_perform(self.task)
        self.task.wait_for_start()
        self.task.complete()

        status = asyncjob_get_progress(jobid)
        assert status == None

    def test_job_progress(self):
        jobid = asyncjob_perform(self.task)
        self.task.wait_for_start()

        self.task.call_from_thread(asyncjob_set_progress, 0, {'hello':'World'})

        status = asyncjob_get_progress(jobid)
        assert status == (0, {'hello':'World'}), status

    def test_job_exception(self):
        jobid = asyncjob_perform(self.task)
        self.task.wait_for_start()

        def _raise():
            raise Exception('ERROR')
        self.task.call_from_thread(_raise)

        status = asyncjob_get_progress(jobid)
        assert status == None
