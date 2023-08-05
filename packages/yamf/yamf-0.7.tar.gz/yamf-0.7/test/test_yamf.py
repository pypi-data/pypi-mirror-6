import sys
import os
sys.path.insert(0, os.path.pardir)

import unittest
import yamf
from yamf import Mock, MockModule, MockArray

class TestMethodCallExpectations(unittest.TestCase):

    def testMockIsCallable(self):
        m = Mock()
        self.assertEquals(m, m(5,k=5))

    def testExpectedMethodCalled(self):
        m = Mock()
        m.method.mustBeCalled
    
        m.method()
        m.verify() 

    def testExpectingCallOnlyOnce(self):
        m = Mock()
        m.method.mustBeCalled.once
    
        m.method()
        m.verify() 

    def testTooManyCalls(self):
        m = Mock()
        m.method.mustBeCalled.once
    
        m.method()
        m.method()
        self.assertRaises(AssertionError, m.verify)

    def testExpectedMethodCalledWithParams(self):
        m = Mock()
        m.method.mustBeCalled
    
        m.method(5)
        m.verify() 

    def testExpectingManyCallsOk(self):
        m = Mock()
        m.method.mustBeCalled.times(2)
    
        m.method()
        m.method()
        m.verify()  
 
    def testExpectedCallsCalledMoreThanExpected(self):
        m = Mock()
        m.method.mustBeCalled.atLeastTimes(2)
    
        m.method()
        m.method()
        m.method()
        m.verify()   

    def testExpectedCallsCalledLessThanExpected(self):
        m = Mock()
        m.method.mustBeCalled.atLeastTimes(2)
    
        m.method()
        self.assertRaises(AssertionError, m.verify)

    def testExpectingManyCallsWithArgsOk(self):
        m = Mock()
        m.method.mustBeCalled.withArgs(5).mustBeCalled.withArgs(6)
    
        # Order is not specified
        m.method(6)
        m.method(5)
        m.verify()

    def testExpectingManyCallsWithArgsFails(self):
        m = Mock()
        m.method.mustBeCalled.withArgs(5).mustBeCalled.withArgs(6)
    
        # Order is not specified
        m.method(5)
        m.method(5)
        self.assertRaises(AssertionError, m.verify)

    def testExpectingManyCallsWithSameArgsFails(self):
        m = Mock()
        m.method.mustBeCalled.withArgs(5).times(2)
    
        m.method(5)
        m.method(6)
        self.assertRaises(AssertionError, m.verify)

    def testExpectingManyCallsWithSameArgsOk(self):
        m = Mock()
        m.method.mustBeCalled.withArgs(5).times(2)
    
        m.method(5)
        m.method(5)
        m.verify()

    def testExpectingManyCallsFails(self):
        m = Mock()
        m.method.mustBeCalled.times(3)
    
        m.method()
        m.method()
        self.assertRaises(AssertionError, m.verify)

    def testAnotherExpectedMethodCalled(self):
        m = Mock()
        m.anotherMethod.mustBeCalled
        
        m.anotherMethod()
        m.verify() 

    def testExpectedMethodNotCalled(self):
        m = Mock()
        m.anotherMethod.mustBeCalled
        
        self.assertRaises(AssertionError, m.verify)

    def testNotExpectedMethodNotCalled(self):
        m = Mock()
        m.method.mustNotBeCalled
        m.verify()

    def testNotExpectedMethodCalled(self):
        m = Mock()
        m.method.mustNotBeCalled
        m.method()
        self.assertRaises(AssertionError, m.verify)      

class TestMethodCallExpectationsWithArguments(unittest.TestCase):
        
    def testExpectedMethodCalledOk(self):
        m = Mock()
        m.method.mustBeCalled.withArgs(5)

        m.method(5)
        m.verify()

    def testExpectedMethodCalledWihtoutArgs(self):
        m = Mock()
        m.method.mustBeCalled.withArgs(5)

        m.method()
        self.assertRaises(AssertionError, m.verify)

    def testExpectedMethodCalledWithWrongArgs(self):
        m = Mock()
        m.method.mustBeCalled.withArgs(5, name='a')

        m.method(5)
        self.assertRaises(AssertionError, m.verify)

class TestReturnValue(unittest.TestCase):
    
    def testSettingReturnValue(self):
        m = Mock()
        m.method.returns(5)

        self.assertEquals( m.method(), 5)

    def testReturnValueWithExpectation(self):
        m = Mock()
        m.method.mustBeCalled.returns(1)

        self.assertEquals(m.method(), 1)
        m.verify()
        
    def testReturnValueWithExpectationCount(self):
        m = Mock()
        m.method.mustBeCalled.once.returns(1)

        self.assertEquals(m.method(), 1)
        m.verify()

    def testReturnValueWithExpectationArgs(self):
        m = Mock()
        m.method.mustBeCalled.withArgs(1).returns(1)

        self.assertEquals(m.method(1), 1)
        m.verify()
        
    def testManyReturnValues(self):
        m = Mock()
        m.method.returns(1).returns(2)
        self.assertEquals(1, m.method())
        self.assertEquals(2, m.method())
        self.assertEquals(2, m.method())

class TestExecuting(unittest.TestCase):
        
    def testExecuting(self):
        m = Mock()
        self.executed = False
        def method(a,b):
            self.executed = True
            
        m.method.execute(method)
        m.method(1,2)
        self.assertTrue(self.executed)

class TestMockingModule(unittest.TestCase):

    def testExpectedModuleMethodCalled(self):
        m = MockModule('os')
        m.getcwd.mustBeCalled
        import os
        os.getcwd()
        m.verify()

    def testModuleMethodReturnValue(self):
        m = MockModule('os')
        m.getcwd.returns('abc123')
        import os
        self.assertEquals(os.getcwd(), 'abc123')
        
    def testMockingWithSetting(self):   
        import os
        m = MockModule(os)
        m.getcwd.returns('test')
        self.assertEquals(os.getcwd(), 'test')



class TestCallHistory(unittest.TestCase):
    
    def testNoCalls(self):
        m = Mock()
        self.assertEquals(m.method.history, [])

    def testCallWithoutArguments(self):
        m = Mock()
        m.method()
        self.assertEquals(m.method.history, [((),{})])

    def testManyCallsWithoutArguments(self):
        m = Mock()
        m.method()
        m.method()
        self.assertEquals(m.method.history, [((), {}),((), {})])

    def testCallWithArguments(self):
        m = Mock()
        m.method(1, 2, k=1, j=2)
        self.assertEquals(m.method.history, [((1, 2), {'k':1, 'j':2})])

    def testManyCallsWithArguments(self):
        m = Mock()
        m.method(1, 2, k=1, j=2)
        m.method(3, 4, k=3, j=4)
        self.assertEquals(m.method.history, [((1, 2), {'k':1, 'j':2}),\
                                             ((3, 4), {'k':3, 'j':4})])
                                            
class TestMockArray(unittest.TestCase):
    
    def testInvalidConstruction(self):
        self.assertRaises(AssertionError, MockArray, 0)
        
    def testOneMockWithExpectationsMet(self):
        mocks = MockArray(1)
        mocks.method.mustBeCalled
        
        mocks[0].method()
        
        mocks.verify()
        
    def testManyMocksWithExpectationsMet(self):
        mocks = MockArray(5)
        mocks.method.mustBeCalled
        
        for mock in mocks: mock.method() 
        
        mocks.verify()
        
    def testOneMockExpectationNotMet(self):
        mocks = MockArray(2)
        mocks.method.mustBeCalled
        
        mocks[1].method()
        self.assertRaises(AssertionError, mocks.verify)      
        
    def testCallCountFails(self): 
        mocks = MockArray(4)
        mocks.method.mustBeCalled.times(5)
        
        for mock in mocks: mock.method() 
        
        self.assertRaises(AssertionError, mocks.verify)      

    def testCallCountOk(self): 
        mocks = MockArray(4)
        mocks.method.mustBeCalled.times(2)
        
        for mock in mocks: mock.method() 
        for mock in mocks: mock.method() 
        
        mocks.verify()

class TestVerifyingManyMocks(unittest.TestCase):

    def testMockFailedVerifcation(self):
        mock = Mock()
        mock.method.mustBeCalled
        self.assertRaises(AssertionError, yamf.verify)
        
    def testVerifyVerifiesOnlyOnes(self):
        mock = Mock()
        mock.method.mustBeCalled
        self.assertRaises(AssertionError, yamf.verify)
        yamf.verify()
        
    def testMockVerifiedIsNotVerifiedWithGlobalVerify(self):
        mock = Mock()
        mock.method.mustBeCalled
        self.assertRaises(AssertionError, mock.verify)
        yamf.verify()
        
        
class TestMockedClassAssertions(unittest.TestCase):
    
    def testMockedClassDoesNotContainAttribute(self):
        class MockedClass:
            pass
        
        mock = Mock(MockedClass)
        
        # assertRaises cannot be used here, because accessing the
        # attribute already throws the assertion error.
        try:
            mock.method
        except AssertionError:
            pass
        
    def testMockedClassContainsAttribute(self):
        class MockedClass:
            def method(self): pass
        
        mock = Mock(MockedClass)
        
    
if __name__ == '__main__':
    unittest.main()
