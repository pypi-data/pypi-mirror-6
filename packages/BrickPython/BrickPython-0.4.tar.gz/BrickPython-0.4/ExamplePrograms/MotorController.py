# Motor Controller
# Example application for using motors.
#
# Copyright (c) 2014 Charles Weir.  Shared under the MIT Licence.

import sys, os # Python path kludge - omit these 2 lines if BrickPython is installed.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0]))))

from BrickPython.TkApplication import TkApplication
from BrickPython.Motor import PIDSetting
from BrickPython.Sensor import Sensor
import logging

class MotorControllerApp(TkApplication):
    '''Application to control a lego NXT motor on port A as a servo motor.

    Type keystrokes into the application window to make the motor move:
    Numbers 0-9 make it move forward the corresponding number of quarter-turns.
    Lower case letters a-p make it go backward the corresponding number of quarter turns.
    Capital letter A stops the motor.
    Capital letters B-G make it go forward at a constant speed.  B is a quarter turn per second, C a half turn, and so on.
    Letters xyz and XYZ adjust the settings for the PID Servo Motor algorithm:
    * X,x increase and decrease the 'distance multiplier' - the P setting.
    * Y,y increase and decrease the 'speed multiplier' - the D setting (I think).
    * Z,z increase and decrease the 'Integrated distance multimplier' - the I setting.
    '''

    def __init__(self):
        TkApplication.__init__(self, {'1': Sensor.ULTRASONIC_CONT })
        self.pidSetting = PIDSetting()

    def rotate(self, degrees):
        'Rotate motor A through *degrees*'
        self.stopAllCoroutines()
        motor = self.motor('A')
        logging.info( "Rotating motor A %d degrees" % degrees )
        co = motor.moveTo( motor.position() + degrees*2 )
        self.addActionCoroutine( co )

    def setSpeed(self, speed):
        'Set the speed of motor A'
        self.stopAllCoroutines()
        motor = self.motor('A')
        logging.info( "Speed for motor A %.2f" % speed )
        co = motor.runAtConstantSpeed( speed )
        self.addActionCoroutine( co )

    def onKeyPress(self, event):
        'Handle user keystroke'
        if TkApplication.onKeyPress(self, event):
            return

        char = event.char
        if char in "0123456789":
            # rotate forwards:
            self.rotate(90 * (ord(char) - ord("0")))
        elif char in "abcdefghijklmnop":
            # rotate reverse:
            self.rotate(-90 * (ord(char) - ord("a") + 1))
        elif char in "ABCDEFG":
            self.setSpeed(180 * (ord(char) - ord("A") ))

        # Adjust PID settings:
        elif char in "xyzXYZ":
            if char == 'x':
                self.pidSetting.distanceMultiplier *= 1.1
            elif char == 'X':
                self.pidSetting.distanceMultiplier /= 1.1
            elif char == 'y':
                self.pidSetting.speedMultiplier *= 1.1
            elif char == 'Y':
                self.pidSetting.speedMultiplier /= 1.1
            elif char == 'z':
                self.pidSetting.integratedDistanceMultiplier *= 1.1
            elif char == 'Z':
                self.pidSetting.integratedDistanceMultiplier /= 1.1
            logging.info( "%r" % (self.pidSetting) )
            self.motor('A').setPIDSetting( self.pidSetting )

if __name__ == "__main__":
    logging.basicConfig(format='%(message)s', level=logging.INFO) # Logging is a simple print
    logging.info( "Starting" )
    app = MotorControllerApp()
    app.mainloop()
