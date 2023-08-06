# James and Charles Weir


import sortOutPythonPaths
from BrickPython.TkApplication import *
import logging

class DoorControlApp(TkApplication):
    '''Application to automatically open and close a door using a proximity sensor.
    It also closes and 'locks' it when C is pressed (so the sensor no longer opens it), starting again when S or O is pressed

    The door is attached to a motor, which opens it by moving through 90 degrees, and closes it the same way.

    The sensor is mounted above the door, so it detects approaching 'peaple'.
    '''

    def __init__(self):
        TkApplication.__init__(self, {PORT_1: TYPE_SENSOR_ULTRASONIC_CONT })
        self.doorLocked = False
        self.addSensorCoroutine( self.openDoorWhenSensorDetected() )

    def openDoorWhenSensorDetected(self):
        '''Coroutine that waits until the sensor detects something nearby, then opens the door, keeps it open for
        4 seconds, then closes it again and repeats.

        It uses the flag *doorLocked* to determine whether the user has 'locked' the door.
        '''
        motorA = self.motor('A')
        sensor1 = self.sensor('1')
        motorA.zeroPosition()
        while True:

            while sensor1.value() > 8 or self.doorLocked:
                yield

            logging.info( "Opening - sensor 1 value is %d" % sensor1.value() )
            for i in motorA.moveTo( -2*90, 2000 ):
                if self.doorLocked: break
                yield


            logging.info( "Waiting 4 seconds" )
            for i in self.waitMilliseconds( 4000 ):
                if self.doorLocked: break
                yield

            logging.info( "Shutting door" )
            for i in motorA.moveTo( 0, 2000 ):
                yield

            logging.info( "Door closed" )

    def onKeyPress(self, event):
        'Handle key input from the user'
        if TkApplication.onKeyPress(self, event):
            return

        char = event.char
        if char in 'Cc':
            logging.info( "Closing and disabling door now" )
            self.doorLocked = True

        elif char in 'SsOo':
            logging.info( "Re-activating door" )
            self.doorLocked = False



if __name__ == "__main__":
    logging.basicConfig(format='%(message)s', level=logging.INFO) # All log messages printed to console.
    logging.info( "Starting" )
    app = DoorControlApp()
    app.mainloop()
