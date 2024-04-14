from typing import List
from workers import WorkerQueue


class QueueState():
    def __init__(self, currentWorker:WorkerQueue, others: List[WorkerQueue]):
        
        self.my_jobs_count = currentWorker.jobs_count()
        self.greater_limit_queue_job_count = 0
        self.lesser_limit_queue_job_count = 0

        for worker in others:
            if worker.get_attribute("limit") is None or worker.get_attribute("limit") > currentWorker.get_attribute("limit"):
                self.greater_limit_queue_job_count += worker.jobs_count()
            else:
                self.lesser_limit_queue_job_count += worker.jobs_count()
    
    def value(self):
        return self.my_jobs_count + self.greater_limit_queue_job_count + self.lesser_limit_queue_job_count

    def __eq__(self, value) -> bool: # type: ignore
        return self.my_jobs_count == value.my_jobs_count and self.greater_limit_queue_job_count == value.greater_limit_queue_job_count and self.lesser_limit_queue_job_count == value.lesser_limit_queue_job_count

    def __hash__(self) -> int:
        return self.my_jobs_count*10000 + self.greater_limit_queue_job_count * 100 + self.lesser_limit_queue_job_count
    
