# Test for BrickPiWrapper

# Run tests as
#   python Test.py
# or, if you've got it installed:
#   nosetests

# Install mock and nosetests on pi or mac using:
#   sudo easy_install nose
#   sudo easy_install mock



from BrickPython.BrickPiWrapper import BrickPiWrapper
from BrickPython.BrickPi import *
import unittest


class TestBrickPiWrapper(unittest.TestCase):

    def testClassExists(self):
        assert(BrickPiWrapper() != None)

    def testAllMethodsOK(self):
        bp = BrickPiWrapper()
        for c in range(ord('A'),ord('D')):
            assert( bp.motor(chr(c)) != None)
        m = bp.motor('A')
        assert( m.power() == 0 )
        assert( m.idChar == 'A' )
        m.setPower(1)
        assert( m.power() == 1 )
        assert( not m.enabled() )
        m.enable( True )
        assert( m.enabled() )
        assert( m.position() != None )
        bp.update()
        s = bp.sensor('1')
        assert( isinstance( s.value(), int ) )
        assert( s.idChar == '1' )

    def testSensorSetup(self):
        bp = BrickPiWrapper( {PORT_1: TYPE_SENSOR_ULTRASONIC_CONT} )
        assert( BrickPi.SensorType[PORT_1] == TYPE_SENSOR_ULTRASONIC_CONT)


if __name__ == '__main__':
    unittest.main()

