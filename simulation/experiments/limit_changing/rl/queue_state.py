from typing import List
from workers import WorkerQueue


class CountsQueueState():
    def __init__(self, currentWorker:WorkerQueue, others: List[WorkerQueue], fromString=False, stringVersion=""):
        
        self.attributes = dict()

        if fromString:
            stringList = stringVersion.split("_")
            self.attributes["my_jobs_count"] = int(stringList[0])
            self.attributes["greater_limit_queue_job_count"] = int(stringList[1])
            self.attributes["lesser_limit_queue_job_count"] = int(stringList[2])
        else:
            self.attributes["my_jobs_count"] = currentWorker.jobs_count()
            self.attributes["greater_limit_queue_job_count"] = 0
            self.attributes["lesser_limit_queue_job_count"] = 0

            for worker in others:
                if worker.get_attribute("limit") is None or worker.get_attribute("limit") > currentWorker.get_attribute("limit"):
                    self.attributes["greater_limit_queue_job_count"] += worker.jobs_count()
                else:
                    self.attributes["lesser_limit_queue_job_count"] += worker.jobs_count()

        
    
    def value(self):
        return self.attributes["my_jobs_count"] + self.attributes["greater_limit_queue_job_count"] + self.attributes["lesser_limit_queue_job_count"]

    def __eq__(self, value) -> bool: # type: ignore
        return self.attributes["my_jobs_count"] == value.attributes["my_jobs_count"] and \
        self.attributes["greater_limit_queue_job_count"] == value.attributes["greater_limit_queue_job_count"] and \
        self.attributes["lesser_limit_queue_job_count"] == value.attributes["lesser_limit_queue_job_count"]

    def __hash__(self) -> int:
        hash = 0
        i = 1
        for key in self.attributes.keys():
            hash += self.attributes[key] *i
            i*=10
        return hash
        
    def __repr__(self):
        return str(self.attributes["my_jobs_count"]) + "_" + str(self.attributes["greater_limit_queue_job_count"]) + "_" + str(self.attributes["lesser_limit_queue_job_count"])
    

class QueueState():

    def get_overloaded_workers(self, workers):
        return filter(lambda w: w.jobs_count() > 1, workers)
    
    def get_empty_workers(self, workers):
        return filter(lambda w: w.jobs_count == 0, workers)


    def __init__(self, currentWorker:WorkerQueue, others: List[WorkerQueue], fromString=False, stringVersion=""):
        
        self.attributes = dict()

        if fromString:
            stringList = stringVersion.split("_")
            self.attributes["my_jobs"] = int(stringList[0])
            self.attributes["empty"] = int(stringList[1])
            self.attributes["overworked"] = int(stringList[2])
        else:
            allWorkers = [currentWorker]
            allWorkers.extend(others)
            self.attributes["overworked"] = len(list(self.get_overloaded_workers(allWorkers)))
            self.attributes["empty"] = len(list(self.get_overloaded_workers(allWorkers)))
            self.attributes["my_jobs"] = currentWorker.jobs_count()

        
    
    def value(self):
        return self.attributes["overworked"]

    def __eq__(self, value) -> bool: # type: ignore
        for attribute in self.attributes.keys():
            if not self.attributes[attribute] == value.attributes[attribute]:
                return False
        return True

    def __hash__(self) -> int:
        hash = 0
        i = 1
        for key in self.attributes.keys():
            hash += self.attributes[key] *i
            i*=10
        return hash
        
    def __repr__(self):
        return str(self.attributes["my_jobs"])+"_"+str(self.attributes["empty"]) + "_" + str(self.attributes["overworked"])