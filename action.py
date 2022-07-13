from typing import List
from states import state

<<<<<<< HEAD
class action:
=======
class action():
>>>>>>> 18943fc (first draft)
    def __init__(self, current_state: state):
       self.current_state = current_state

    def determine_next_state(self, states: List[state]) -> state:
        if states.index(self.current_state) < len(states) -1:
            return states[states.index(self.current_state) +1 ]
        return self.state_choice
        # asumming we only move forward. doesn't take buttons into account yet but we can point to prior states

