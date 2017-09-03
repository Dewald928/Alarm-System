# ===============================================
# IMPLEMENTATION

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


if __name__ == '__main__':
    r = RobotMaid()
    for i in range(10):
        startTime = clock()
        timeInterval = 1
        while (startTime + timeInterval > clock()):
            pass
        r.Execute()
    print('Exiting program...')