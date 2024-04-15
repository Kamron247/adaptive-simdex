from interfaces import AbstractSelfAdaptingStrategy
from logger import logWorkers, sampleLog
from experiments.limit_changing.limit_changing_interface import DynamicLimitAbstractSelfAdaptingStrategy
from experiments.limit_changing.rl.rl_brain import INCREASE, DECREASE, MAINTAIN, Brain
from experiments.limit_changing.rl.queue_state import QueueState
   
class ReinforcementLearningLimitChangingSelfAdaptingStrategy(DynamicLimitAbstractSelfAdaptingStrategy):
    """Represents a SA controller that uses simple machine learning.

    Collects job and ref. job metadata to compute categorized statistics of job duration based on their
    affiliation to exercises and runtimes. These statistics are used by dispatcher for predicting the duration
    of incomming jobs.

    If there is a larger queue with at least three items in it and this queue is empty increase
    the limit by x seconds

    If there is an empty larger queue decrease the limit by x seconds
    """

    def __init__(self, max_long_queues, ref_jobs):
        super().__init__(max_long_queues, ref_jobs)
        self.brain = Brain()
        self.previous_moves = dict()


    def get_overloaded_workers(self, workers):
        return filter(lambda w: w.jobs_count() > 1, workers)
    
    def get_empty_workers(self, workers):
        return filter(lambda w: w.jobs_count == 0, workers)
    
    def update_worker_limit(self, worker, all_workers):

        if worker in self.previous_moves.keys() and self.previous_moves[worker] is not None:
            self.learn_from_previous_move(worker, all_workers)

        worker_state = QueueState(worker, all_workers)
        action = self.brain.think(worker_state)

        if action == INCREASE:
            self.increase_worker_limit(worker)
        elif action == DECREASE:
            self.decrease_worker_limit(worker)

        self.previous_moves[worker] = [worker_state, action]

        logWorkers(all_workers)

    def learn_from_previous_move(self, worker, all_workers):
        new_state = QueueState(worker, all_workers)
        old_state = self.previous_moves[worker][0]
        action = self.previous_moves[worker][1]


        if new_state.value() == 0 and old_state.value() == 0 and action == INCREASE:
            reward = -1
        else:
            reward = old_state.value() - new_state.value()


        self.brain.learn(new_state, old_state, action, reward)
        self.previous_moves[worker] = None
              

    
 