# Actions = [stay the same, increase queue limit, decrease queue limit]
import random
import csv

from experiments.limit_changing.rl.queue_state import QueueState

INCREASE = 1
DECREASE = 2
MAINTAIN = 0
class Brain():

    def __init__(self, gamma, learning_rate):
        self.q_values = dict()
        self.learning_rate = learning_rate
        self.gamma = gamma


    def add_state_to_q_values(self, state):
        self.q_values[state] = [0, 0, 0]

    def bestActionFromState(self, state):
        maxValue = max(filter(lambda v: v is not None, self.q_values[state]))
        maxValueAction = self.q_values[state].index(max(filter(lambda v: v is not None,self.q_values[state])))
        return maxValueAction, maxValue

    def think(self, state):
        if state in self.q_values.keys():
            return self.q_values[state].index(max(filter(lambda v: v is not None,self.q_values[state])))
        else:
            self.add_state_to_q_values(state)
            return random.randrange(0,3)
 
    def learn(self, newState, oldState, action, reward):
        if newState not in self.q_values.keys():
            self.add_state_to_q_values(newState)
        prev_q = (1-self.learning_rate)*self.q_values[oldState][action]
        new_q = self.learning_rate*(reward + self.gamma * self.q_values[newState][self.think(newState)])
        self.q_values[oldState][action] = round(prev_q + new_q, 5)

    def memorize(self, filename):
        with open(filename, "w") as file:
            for state in self.q_values.keys():
                file.write(repr(state))
                for value in self.q_values[state]:
                    file.write(","+ str(value))
                file.write("\n")
    
    def remember(self, filename):
        with open(filename, "r") as csvfile:
            reader = csv.reader(csvfile)
            for line in reader:
                state = QueueState(None, None, True, line[0])
                self.q_values[state] = list(map(lambda s: float(s), line[1:]))
