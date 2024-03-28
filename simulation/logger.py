
DEBUG = False
INDEX = 0
def log(logline, end="\n"):
    if DEBUG:
        print(logline,end=end)

def logWorker(worker):
    log(f"Worker:{worker.attributes}", end=" -- ")

def logWorkers(workers):
    for worker in workers:
        logWorker(worker)
    log("")

def sampleLog(workers):
    global INDEX
    if INDEX % 10000 == 0:
        logWorkers(workers)
    INDEX+=1