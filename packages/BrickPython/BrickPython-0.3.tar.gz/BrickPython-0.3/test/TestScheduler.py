# Tests for Scheduler
#
# Copyright (c) 2014 Charles Weir.  Shared under the MIT Licence.

# Run tests as
#   python TestScheduler.py
# or, if you've got it installed:
#   nosetests



from BrickPython.BrickPiWrapper import *
import unittest
from mock import *

class TestScheduler(unittest.TestCase):
    ''' Tests for the Scheduler class, its built-in coroutines, and its coroutine handling.
    '''
    coroutineCalls = []
    @staticmethod
    def dummyCoroutine(start = 1, finish = 5):
        for i in range(start, finish):
            TestScheduler.coroutineCalls.append(i)
            yield

    @staticmethod
    def dummyCoroutineThatDoesCleanup(start = 1, finish = 2):
        for i in range(start, finish):
            TestScheduler.coroutineCalls.append(i)
            try:
                yield
            finally:
                TestScheduler.coroutineCalls.append( -1 )

    @staticmethod
    def dummyCoroutineThatTakesTime():
        for i in range(0,2):
            for j in range (0,10): # Takes 10 ms
                Scheduler.currentTimeMillis() # Increments the mock time.
            yield

    @staticmethod
    def dummyCoroutineThatThrowsException():
        raise Exception()
        yield

    @staticmethod
    def checkCoroutineFinished(coroutine):
        # Fails the test if the given coroutine hasn't finished.
        try:
            coroutine.next()
            assert(False)
        except StopIteration:
            pass


    def setUp(self):
        TestScheduler.coroutineCalls = []
        self.scheduler = Scheduler()
        # Yes - we can use @Patch to do the following for specific tests, but that fails horribly when
        # tests are run as python setup.py test
        self.saveCurrentTimeMillis = Scheduler.currentTimeMillis
        Scheduler.currentTimeMillis =  Mock( side_effect = xrange(0,10000) ) # Each call answers the next integer

        def tearDown(self):
            Scheduler.currentTimeMillis = self.saveCurrentTimeMillis

    def testCoroutinesGetCalledUntilDone(self):
        # When we start a motor coroutine
        coroutine = TestScheduler.dummyCoroutine()
        self.scheduler.addActionCoroutine(coroutine)
        # and run it until complete
        for i in range(0,10):
            self.scheduler.doWork()
        # It has completed and no coroutines are running
        assert( TestScheduler.coroutineCalls[-1] == 4 )
        TestScheduler.checkCoroutineFinished( coroutine )
        assert( self.scheduler.numCoroutines() == 0)

    def testCoroutinesGetCleanedUp(self):
        # When we start a motor coroutine
        coroutine = TestScheduler.dummyCoroutineThatDoesCleanup()
        self.scheduler.addActionCoroutine(coroutine)
        # and run it until complete
        for i in range(0,10):
            self.scheduler.doWork()
        # It has cleaned up
        self.assertEquals( TestScheduler.coroutineCalls[-1],	 -1 )

    def testCoroutinesCanBeTerminated(self):
        # When we start a motor coroutine
        coroutine = TestScheduler.dummyCoroutine()
        self.scheduler.addActionCoroutine(coroutine)
        # run it a bit, then terminate it
        self.scheduler.doWork()
        self.scheduler.stopCoroutine( coroutine )
        self.scheduler.doWork()
        # It has completed early
        assert( TestScheduler.coroutineCalls[-1] == 1 )
        TestScheduler.checkCoroutineFinished( coroutine )

    def testAllCoroutinesCanBeTerminated(self):
        # When we start two coroutines
        for i in range(2):
            self.scheduler.addActionCoroutine(TestScheduler.dummyCoroutine())
        # run them, then terminate them all
        self.scheduler.doWork()
        self.scheduler.stopAllCoroutines()
        self.scheduler.doWork()
        self.scheduler.doWork()
        # They all terminate
        assert( TestScheduler.coroutineCalls == [1 , 1] )

    def testCoroutineThatThrowsException(self):
        # When we have a coroutine that throws an exception:
        self.scheduler.addActionCoroutine(TestScheduler.dummyCoroutineThatThrowsException())
        # then the scheduler will remove it from the work schedule
        self.scheduler.doWork()
        assert( self.scheduler.numCoroutines() == 0 )

    def testCoroutinesCanCleanupWhenTerminated(self):
        # When we start a motor coroutine
        coroutine = TestScheduler.dummyCoroutineThatDoesCleanup()
        self.scheduler.addActionCoroutine(coroutine)
        # run it a bit, then terminate it
        self.scheduler.doWork()
        self.scheduler.stopCoroutine( coroutine )
        self.scheduler.doWork()
        # It has completed and cleaned up
        assert( TestScheduler.coroutineCalls[-1] == -1 )
        TestScheduler.checkCoroutineFinished( coroutine )

    def testSensorCoroutinesWork(self):
        # When we start a sensor coroutine
        self.scheduler.addSensorCoroutine(TestScheduler.dummyCoroutine())
        # it gets executed
        self.scheduler.doWork()
        assert( TestScheduler.coroutineCalls[-1] == 1 )

    def testSensorCoroutinesCanBeAccessedAndGetDoneFirst(self):
        # When we start a motor coroutine (starts at 2) and a sensor one (starts at 1)
        sensorCo = TestScheduler.dummyCoroutine()
        motorCo = TestScheduler.dummyCoroutine(2)
        motorCoReturned = self.scheduler.addActionCoroutine(motorCo)
        sensorCoReturned = self.scheduler.addSensorCoroutine(sensorCo)
        # Then the 'latest coroutine' of each time will be returned correctly:
        self.assertEquals( motorCoReturned, motorCo )
        self.assertEquals( sensorCoReturned, sensorCo )
        # and the motor coroutine will update the status last:
        self.scheduler.doWork()
        self.assertEquals( TestScheduler.coroutineCalls[-1], 2 )

    def testUpdateCoroutineGetsCalledBothBeforeAndAfterTheOtherCoroutines(self):
        # When we start a motor and sensor coroutines (start at 1,4) with an update one (starts at 10)
        self.scheduler.setUpdateCoroutine(TestScheduler.dummyCoroutine(10,20))
        self.scheduler.addSensorCoroutine(TestScheduler.dummyCoroutine(4,8))
        self.scheduler.addActionCoroutine(TestScheduler.dummyCoroutine())
        # then the update coroutine will be invoked before and after the others:
        self.scheduler.doWork()
        assert( TestScheduler.coroutineCalls == [10,4,1,11] )

    def testWaitMilliseconds(self):
        # If we wait for 10 ms
        for i in self.scheduler.waitMilliseconds(10):
            pass
        # that's about the time that will have passed:
        assert( self.scheduler.currentTimeMillis() in range(10,12) )

    def testRunTillFirstCompletes(self):
        # When we run three coroutines using runTillFirstCompletes:
        for i in self.scheduler.runTillFirstCompletes(TestScheduler.dummyCoroutine(1,9),
                                                      TestScheduler.dummyCoroutine(1,2),
                                                      TestScheduler.dummyCoroutine(1,9) ):
            self.scheduler.doWork()
        #  the first to complete stops the others:
        self.assertEquals( TestScheduler.coroutineCalls, [1,1,1,2] )
        self.assertEquals( self.scheduler.numCoroutines(), 0)

    def testRunTillAllComplete( self ):
        # When we run three coroutines using runTillAllComplete:
        for i in self.scheduler.runTillAllComplete( *[TestScheduler.dummyCoroutine(1,i) for i in [2,3,4]] ):
            self.scheduler.doWork()
        #  they all run to completion:
        print TestScheduler.coroutineCalls
        assert( TestScheduler.coroutineCalls == [1,1,1,2,2,3] )
        assert( self.scheduler.numCoroutines() == 0)

    def testWithTimeout(self):
        # When we run a coroutine with a timeout:
        for i in self.scheduler.withTimeout(10, TestScheduler.dummyCoroutineThatDoesCleanup(1,99) ):
            self.scheduler.doWork()
        # It completes at around the timeout, and does cleanup:
        print TestScheduler.coroutineCalls
        self.assertTrue( 0 < TestScheduler.coroutineCalls[-2] <= 10) # N.b. currentTimeMillis is called more than once per doWork call.
        self.assertEquals( TestScheduler.coroutineCalls[-1], -1 )

    def testTimeMillisToNextCall(self):
        # Given a mock timer, and a different scheduler set up with a known time interval
        scheduler = Scheduler(20)
        # when we have just coroutines that take no time
        scheduler.addActionCoroutine( TestScheduler.dummyCoroutine() )
        # then the time to next tick is the default less a bit for the timer check calls:
        scheduler.doWork()
        ttnt = scheduler.timeMillisToNextCall()
        assert( ttnt in range(17,20) )
        # when we have an additional coroutine that takes time
        scheduler.addSensorCoroutine( TestScheduler.dummyCoroutineThatTakesTime() )
        # then the time to next tick is less by the amount of time taken by the coroutine:
        scheduler.doWork()
        ttnt = scheduler.timeMillisToNextCall()
        assert( ttnt in range(7,10) )
        # but when the coroutines take more time than the time interval available
        for i in range(0,2):
            scheduler.addSensorCoroutine( TestScheduler.dummyCoroutineThatTakesTime() )
        # the time to next tick never gets less than zero
        scheduler.doWork()
        ttnt = scheduler.timeMillisToNextCall()
        assert( ttnt == 0 )
        # and incidentally, we should have all the coroutines still running
        assert( scheduler.numCoroutines() == 4 )

    def timeCheckerCoroutine(self):
        # Helper coroutine for testEachCallToACoroutineGetsADifferentTime
        # Checks that each call gets a different time value.
        time = Scheduler.currentTimeMillis()
        while True:
            yield
            newTime = Scheduler.currentTimeMillis()
            self.assertNotEquals( newTime, time )
            time = newTime

    def testEachCallToACoroutineGetsADifferentTime(self):
        scheduler = Scheduler()
        Scheduler.currentTimeMillis =  Mock( side_effect = [0,0,0,0,0,0,0,0,0,0,1,2,3,4,5] )
        # For any coroutine,
        scheduler.setUpdateCoroutine( self.timeCheckerCoroutine() )
        # We can guarantee that the timer always increments between calls (for speed calculations etc).
        for i in range(1,10):
            scheduler.doWork()

    def testTheWaitForCoroutine(self):
        scheduler = Scheduler()
        arrayParameter = []
        # When we create a WaitFor coroutine with a function that takes one parameter (actually an array)
        coroutine = scheduler.waitFor( lambda ap: len(ap) > 0, arrayParameter )
        # It runs
        for i in range(0,5):
            coroutine.next()
        # Until the function returns true.
        arrayParameter.append(1)
        TestScheduler.checkCoroutineFinished( coroutine )


if __name__ == '__main__':
    unittest.main()

