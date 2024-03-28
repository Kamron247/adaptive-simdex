from interfaces import AbstractSelfAdaptingStrategy
from logger import logWorkers, sampleLog

def decrease_worker_limit(adaptive_worker):
        if adaptive_worker.get_attribute("limit")-adaptive_worker.get_attribute("aggression") < adaptive_worker.get_attribute("limit-min"):
            adaptive_worker.set_attribute("limit", adaptive_worker.get_attribute("limit-min"))
        else:
            adaptive_worker.set_attribute("limit", adaptive_worker.get_attribute("limit")-(adaptive_worker.get_attribute("aggression")*.75))
    
def increase_worker_limit(worker):
    worker.set_attribute("limit", worker.get_attribute("limit")+worker.get_attribute("aggression"))



class LimitChangingCategorySelfAdaptingStrategy(AbstractSelfAdaptingStrategy):
    """Represents a SA controller that uses simple machine learning.

    Collects job and ref. job metadata to compute categorized statistics of job duration based on their
    affiliation to exercises and runtimes. These statistics are used by dispatcher for predicting the duration
    of incomming jobs.

    If there is a larger queue with at least three items in it and this queue is empty increase
    the limit by x seconds

    If there is an empty larger queue decrease the limit by x seconds
    """

    def __init__(self, max_long_queues, ref_jobs):
        self.max_long_queues = max_long_queues
        self.ref_jobs = ref_jobs[:]
        self.ref_jobs.reverse()

    def _update_dispatcher(self, ts, dispatcher):
        while len(self.ref_jobs) > 0 and self.ref_jobs[-1].spawn_ts + self.ref_jobs[-1].duration <= ts:
            job = self.ref_jobs.pop()
            if job.compilation_ok:
                dispatcher.add_ref_job(job)

    def init(self, ts, dispatcher, workers):
        self._update_dispatcher(ts, dispatcher)

    def do_adapt(self, ts, dispatcher, workers, job=None):
        self._update_dispatcher(ts, dispatcher)

        workers.sort(key=lambda w: w.get_attribute("limit") == None, reverse=True )
        adaptive_limits = []
        overloaded = []
        empty = []

        for i in range(len(workers)):
            worker = workers[i]
            if worker.get_attribute("dynamic-limit"):
                adaptive_limits.append(worker)
            if worker.jobs_count() > 1:
                overloaded.append(worker)
            if worker.jobs_count() == 0:
                empty.append(worker)

        higherLimitLambda = lambda w: w.get_attribute("limit") is None or w.get_attribute("limit") > adaptive_worker.get_attribute("limit")
        
        for adaptive_worker in adaptive_limits:
            higherLimitsOverloaded = tuple(filter(higherLimitLambda, overloaded))
            higherLimitsEmpty = tuple(filter(higherLimitLambda, empty))
            if len(higherLimitsOverloaded) > 0:
                increase_worker_limit(adaptive_worker)
                logWorkers(workers)
            elif len(higherLimitsEmpty) > 0 and adaptive_worker.get_attribute("limit") > adaptive_worker.get_attribute("limit-min"):
                decrease_worker_limit(adaptive_worker)
                logWorkers(workers)

        sampleLog(workers)
            

        if (job and job.compilation_ok):
            dispatcher.add_ref_job(job)

    