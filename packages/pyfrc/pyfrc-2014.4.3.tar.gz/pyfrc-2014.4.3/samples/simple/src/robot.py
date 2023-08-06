
try:
    import wpilib
except ImportError:
    from pyfrc import wpilib

class MyRobot(wpilib.SimpleRobot):

    def __init__(self):
        super().__init__()
        
        self.stick = wpilib.Joystick(1)
        
        # two wheel drive
        l_motor = wpilib.Jaguar(1)
        r_motor = wpilib.Jaguar(2)
        self.drive = wpilib.RobotDrive(l_motor, r_motor)

    def Autonomous(self):
        '''Called when autonomous mode is enabled'''
        
        timer = wpilib.Timer()
        timer.Start()
        done = False
        
        self.GetWatchdog().SetEnabled(False)
        while self.IsAutonomous() and self.IsEnabled():
            
            if not done and not timer.HasPeriodPassed(5):
                self.drive.ArcadeDrive(0.4, 0)
            else:
                self.drive.ArcadeDrive(0, 0)
                done = True
            
            wpilib.Wait(0.01)

    def OperatorControl(self):
        '''Called when operation control mode is enabled'''
        
        dog = self.GetWatchdog()
        dog.SetEnabled(True)
        dog.SetExpiration(0.25)

        timer = wpilib.Timer()
        timer.Start()

        while self.IsOperatorControl() and self.IsEnabled():
            dog.Feed()
            self.drive.ArcadeDrive(self.stick)
            wpilib.Wait(0.04)

def run():
    '''Called by RobotPy when the robot initializes'''
    
    robot = MyRobot()
    robot.StartCompetition()
    
    return robot


if __name__ == '__main__':
    wpilib.run()

