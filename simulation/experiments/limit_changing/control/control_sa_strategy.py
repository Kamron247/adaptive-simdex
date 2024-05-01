from logger import sampleLog
from simple_pid import PID
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

    def __init__(self, max_long_queues, ref_jobs, *args):
        super().__init__(max_long_queues, ref_jobs)
        self.pids = dict()
    
    def update_worker_limit(self, worker, all_workers):  
        if worker not in self.pids.keys():
            min = worker.get_attribute("limit-min")/10
            max = worker.get_attribute("limit-max")/10
            self.pids[worker] = PID(0.9, 0.4, 0, setpoint=0.3, starting_output=(min+max)/2)
            self.pids[worker].output_limits = (worker.get_attribute("limit-min")/10, worker.get_attribute("limit-max")/10)

        jobs = worker.jobs_count()
        set_value = self.pids[worker](jobs)

        self.set_worker_limit(worker, set_value*10)

        sampleLog(all_workers)
              