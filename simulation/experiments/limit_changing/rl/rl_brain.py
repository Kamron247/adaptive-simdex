# Actions = [stay the same, increase queue limit, decrease queue limit]
import random

INCREASE = 1
DECREASE = 2
MAINTAIN = 0
class Brain():

    def __init__(self):
        self.q_values = dict()
        self.learning_rate = 0.9
        self.gamma = 0.5


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
        self.q_values[oldState][action] = prev_q + new_q
