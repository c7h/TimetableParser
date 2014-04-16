'''
Created on 16.04.2014

@author: christoph
'''
import unittest
from stundenplanparser.stundenplanparser import Timetableparser
from datetime import date

class Test(unittest.TestCase):

    def setUp(self):
        self.tp = Timetableparser()


    def testSemesterID_01(self):
        
        bounds= {date(2014, 3, 14): 22, #ws
                 date(2014, 3, 15): 23, #ss
                 date(2014, 9, 30): 23, #ss
                 date(2014, 10, 1): 24, #ws
                 }
        
        
        for adate, expected_semester in bounds.iteritems():
            result = self.tp.getSemesterIDforDate(adate)
            print "testing date %s == semester %i" % (adate.isoformat(), expected_semester)
            self.assertEqual(result, 
                             expected_semester, 
                             "expected semester %i but got %d for date %s" % (expected_semester, result, adate.isoformat())
                             )
            
        
    def testSemesterID_02(self):
        adate = date(2014, 4, 16)
        result = self.tp.getSemesterIDforDate(adate)
        self.assertEqual(result, 23, "expected 23 got %s" % str(result))
        


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testSemesterID_01']
    unittest.main()
