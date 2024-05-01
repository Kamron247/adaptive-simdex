from interfaces import AbstractSelfAdaptingStrategy
from rich.progress import Progress, TextColumn, BarColumn, MofNCompleteColumn, TimeRemainingColumn, Column

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
        self.progressBars = {}
        self.progress =  Progress(TextColumn("[progress.description]{task.description}"), BarColumn(), MofNCompleteColumn(), TextColumn("Jobs: {task.fields[jobs]}"))
        i = 1
       
        for worker in workers:
            
            if (worker.get_attribute("limit-max") is not None):
                task = self.progress.add_task(f"[cyan]Dynamic Limit Worker {i}", total=worker.get_attribute("limit-max"), jobs=0)
                self.progressBars[worker] = task
            elif (worker.get_attribute("limit") is not None):
                task = self.progress.add_task(f"Static Limit Worker {i}", total=worker.get_attribute("limit"), jobs=0)
                self.progress.update(task, completed=worker.get_attribute("limit") )
                self.progressBars[worker] = task
            else:
                task = self.progress.add_task(f"Infinite Limit Worker {i}", total=0, jobs=0)
                self.progress.update(task, completed=0)
                self.progressBars[worker] = task
            i+=1
        self.progress.start()



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

    def set_worker_limit(self, adaptive_worker, set_value):
        if adaptive_worker.get_attribute("limit-max") < set_value:
            adaptive_worker.set_attribute("limit", adaptive_worker.get_attribute("limit-max")) 

        elif adaptive_worker.get_attribute("limit-min") > set_value:
            adaptive_worker.set_attribute("limit", adaptive_worker.get_attribute("limit-min")) 

        else:
            adaptive_worker.set_attribute("limit", set_value) 

    def update_worker_limit(self, worker, other_workers):
        raise NotImplementedError
    

    def render(self, workers):
        for worker in workers:
            self.progress.update(self.progressBars[worker], completed=worker.get_attribute("limit"), jobs=worker.jobs_count())

    

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
        self.render(workers)

    