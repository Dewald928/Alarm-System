# ===============================================
# IMPLEMENTATION
from StateMachine import FSM
# from States import State
from States import Sleep
from States import CleanDishes
from States import Vacuum
from States import Transition


Char = type("Char", (object,), {})


class RobotMaid(Char):
    ''' Base character which will be holding the Finite State Machine,
        which in turn will hold the states and transitions. '''

    def __init__(self):
        self.FSM = FSM(self)

        ## STATES
        self.FSM.AddState("Sleep", Sleep(self.FSM))
        self.FSM.AddState("CleanDishes", CleanDishes(self.FSM))
        self.FSM.AddState("Vacuum", Vacuum(self.FSM))

        ## TRANSITIONS
        self.FSM.AddTransition("toSleep", Transition("Sleep"))
        self.FSM.AddTransition("toVacuum", Transition("Vacuum"))
        self.FSM.AddTransition("toCleanDishes", Transition("CleanDishes"))

        self.FSM.SetState("Sleep")

    def Execute(self):
        self.FSM.Execute()