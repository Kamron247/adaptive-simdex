from interfaces import AbstractSelfAdaptingStrategy


class DynamicLimitAbstractSelfAdaptingStrategy(AbstractSelfAdaptingStrategy):
    """Represents the controller used for self-adaptation of the system.

    The main part is hidden into do_adapt() method that is used both for monitoring (collecing data)
    and for adaptation (modifying the system configuration).
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


    def get_updateable_workers(self, workers):
        return filter(lambda w: w.get_attribute("dynamic-limit"), workers)

    def decrease_worker_limit(self, adaptive_worker):
        if adaptive_worker.get_attribute("limit")-adaptive_worker.get_attribute("aggression") < adaptive_worker.get_attribute("limit-min"):
            adaptive_worker.set_attribute("limit", adaptive_worker.get_attribute("limit-min"))
        else:
            adaptive_worker.set_attribute("limit", adaptive_worker.get_attribute("limit")-(adaptive_worker.get_attribute("aggression")*.75))
    
    def increase_worker_limit(self, adaptive_worker):
        if adaptive_worker.get_attribute("limit")+adaptive_worker.get_attribute("aggression") > adaptive_worker.get_attribute("limit-max"):
            adaptive_worker.set_attribute("limit", adaptive_worker.get_attribute("limit-max"))
        else:
            adaptive_worker.set_attribute("limit", adaptive_worker.get_attribute("limit")+adaptive_worker.get_attribute("aggression"))


    def update_worker_limit(self, worker, other_workers):
        raise NotImplementedError
    
    

    def do_adapt(self, ts, dispatcher, workers, job=None):
        """The main interface method called from the simulation.

        The method is called periodically (with job == None) and when new job is spawned
        (right before the job is dispatched).
        The ts holds simulation time, dispatcher and workers are the main objects of the simulation.
        The do_adapt() call may choose to modify dispatcher and workers settings to change simulation behavior.
        The workers use generic atribute abstraction, dispatcher is implemented along with the SA strategy,
        so the user may design whatever interface is necessary between these two modules.
        """
        self._update_dispatcher(ts, dispatcher)
        updateable_workers = self.get_updateable_workers(workers)
        for worker in updateable_workers:
            self.update_worker_limit(worker, workers)

        if (job and job.compilation_ok):
           dispatcher.add_ref_job(job)
    