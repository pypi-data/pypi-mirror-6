import sys
import os
sys.path.insert(0, os.path.pardir)
import unittest
from yamf import ReturnValues

class TestReturnValue(unittest.TestCase):
    
    def testNoneIsReturnedByDefault(self):
        r = ReturnValues()
        self.assertEquals(None, r.getNext())
        
    def testSetValueIsReturned(self):
        r = ReturnValues()
        r.add(5)
        self.assertEquals(5, r.getNext())
        
    def testLastSetValueIsReturnedForever(self):
        r = ReturnValues()
        r.add(5)
        for i in range(0, 5):
            self.assertEquals(5, r.getNext())
            
    def testAllAddedValuesAreReturned(self):
        r = ReturnValues()
        r.add(5)
        r.add(6)
        self.assertEquals(5, r.getNext())
        self.assertEquals(6, r.getNext())
        
        

if __name__ == '__main__':
    unittest.main()

