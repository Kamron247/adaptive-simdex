
from workers import WorkerQueue


DEBUG = False
INDEX = 0
def log(logline, end="\n"):
    if DEBUG:
        print(logline,end=end)

def logWorker(worker:WorkerQueue):
    log(f"\tWorker:{worker.attributes}, Jobs:{worker.jobs_count()}", end="\n")

def logWorkers(workers):
    log("Workers:")
    for worker in workers:
        logWorker(worker)
    log("")

def sampleLog(workers):
    global INDEX
    if INDEX % 10000 == 0:
        logWorkers(workers)
    INDEX+=1