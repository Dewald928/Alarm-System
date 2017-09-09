# ===============================================
# IMPLEMENTATION
from StateMachine import FSM
# from States import State
from States import Disarmed
from States import Armed
from States import Transition


Char = type("Char", (object,), {})


class Alarm(Char):
    ''' Base character which will be holding the Finite State Machine,
        which in turn will hold the states and transitions. '''

    def __init__(self):
        self.FSM = FSM(self)

        # STATES
        self.FSM.AddState("Disarmed", Disarmed(self.FSM))
        self.FSM.AddState("Armed", Armed(self.FSM))

        # TRANSITIONS
        self.FSM.AddTransition("toDisarmed", Transition("Disarmed"))
        self.FSM.AddTransition("toArmed", Transition("Armed"))

        self.FSM.SetState("Disarmed")

    def Execute(self):
        self.FSM.Execute()