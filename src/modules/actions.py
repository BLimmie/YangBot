from platform import machine
from typing import List
from states import state

'''
Idea for action:

Action represents a button and what will happen upon interaction. It is responsible for manipulating data and creating a new state. 
It will then pass this state onto machine, which will update itself accordingly.
'''

class action:
    def __init__(self, current_state: state):
       self.current_state = current_state

    def determine_next_state(self, states: List[state]) -> state:
        if states.index(self.current_state) < len(states) -1:
            return states[states.index(self.current_state) +1 ]
        return self.state_choice
        # asumming we only move forward. doesn't take buttons into account yet but we can point to prior states