from interfaces import AbstractSelfAdaptingStrategy
from logger import logWorkers, sampleLog
from experiments.limit_changing.limit_changing_interface import DynamicLimitAbstractSelfAdaptingStrategy
   
class LimitChangingCategorySelfAdaptingStrategy(DynamicLimitAbstractSelfAdaptingStrategy):
    """Represents a SA controller that uses simple machine learning.

    Collects job and ref. job metadata to compute categorized statistics of job duration based on their
    affiliation to exercises and runtimes. These statistics are used by dispatcher for predicting the duration
    of incomming jobs.

    If there is a larger queue with at least three items in it and this queue is empty increase
    the limit by x seconds

    If there is an empty larger queue decrease the limit by x seconds
    """

    def get_overloaded_workers(self, workers):
        return filter(lambda w: w.jobs_count() > 1, workers)
    
    def get_empty_workers(self, workers):
        return filter(lambda w: w.jobs_count == 0, workers)
    
    def update_worker_limit(self, worker, all_workers):
        overloaded = self.get_overloaded_workers(all_workers)
        empty = self.get_empty_workers(all_workers)

        higherLimitLambda = lambda w: w.get_attribute("limit") is None or w.get_attribute("limit") > worker.get_attribute("limit")
        
        higherLimitsOverloaded = tuple(filter(higherLimitLambda, overloaded))
        higherLimitsEmpty = tuple(filter(higherLimitLambda, empty))
        if len(higherLimitsOverloaded) > 0:
            self.increase_worker_limit(worker)
            logWorkers(all_workers)
        elif len(higherLimitsEmpty) > 0 and worker.get_attribute("limit") > worker.get_attribute("limit-min"):
            self.decrease_worker_limit(worker)
            logWorkers(all_workers)

        sampleLog(all_workers)
              