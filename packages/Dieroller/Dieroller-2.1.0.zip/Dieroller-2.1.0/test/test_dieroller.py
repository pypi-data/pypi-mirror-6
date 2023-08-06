"""DieRollerTest.py
"""

__py_version = 2.6
__version = 1
__author__= "Josh English"

import unittest


import dieroller as dr

class DieRollerTestCase(unittest.TestCase):
    goodrolls = (
            ('d4', [1,2,3,4]),
            ('2d4',[2,3,4,5,6,7,8]),
            ('3d6',range(3,19)),
            ('4d8-3',range(1,30)),
            ('2d10+1',range(3,22)),
            ('5d6x3',range(15,155,3)),
            ('d0+2', [2])
            )
    badrolls = (
        ('6', "Missing the letter d"),
        ('d7+', "Has operation but no adjustment"),
        ('3d', "Missing the size of the die"),
        ('d20a5', "Strange operator"),

        #~ ('4d6^4',"Bad operator"), this test doesn't work, because I can't get the regular expression to work
        )

    def test_BadDieRoll(self):
        """rolldie should fail with bad string"""
        for roll, reason in self.badrolls:
            self.assertRaises(dr.RollError,dr.rolldice,roll)

    def test_GoodRolls(self):
        """rolldie should pass good rolls in the proper range"""
        for roll,ran in self.goodrolls:
            for x in range(100):
                self.failIf(dr.rolldice(roll) not in ran)

    def test_checkGoodRolls(self):
        """checkroll should accept good die rolls"""
        for roll,ran in self.goodrolls:
            self.failUnless(dr.checkroll(roll))

    def test_checkBadRolls(self):
        """checkroll should return False on bad die rolls"""
        for roll, reason in self.badrolls:
            self.failIf(dr.checkroll(roll))

    def test_listroll(self):
        """listroll should return appropriate values"""
        roll = dr.listroll('100d10')
        for r in roll:
            self.failUnless(0 < r < 11)

def test_main():
    test_support.run_unittest(DieRollerTestCase)

if __name__=='__main__':
    unittest.main()
