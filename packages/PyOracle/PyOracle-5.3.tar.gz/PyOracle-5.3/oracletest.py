'''
oracletest.py
test file for PyOracle and FactOracle 

Copyright (C) 12.02.2013 Cheng-i Wang 

This file is part of PyOracle.

PyOracle is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

PyOracle is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with PyOracle.  If not, see <http://www.gnu.org/licenses/>.
'''

import unittest
import Resources.PyOracle.PyOracle as po
import Resources.PyOracle.FactOracle as fo

class SymbolicSequence(unittest.TestCase):

    seq1 = [    'a','a','b','b','a','b','b','a','b','b','a','b']
    lrs1 = [ 0 , 0 , 1 , 0 , 1 , 1 , 2 , 3 , 4 , 5 , 6 , 7 , 8 ]
    code1 = [(0, 'a'), (1, 1), (0, 'b'), (1, 3), (8, 2)]
    seq2 = [    'a','b','b','c','a','b','c','d','a','b','c']
    lrs2 = [ 0 , 0 , 0 , 1 , 0 , 1 , 2 , 2 , 0 , 1 , 2 , 2 ]
    code2 = [(0, 'a'), (0, 'b'), (1, 2), (0, 'c'), (2, 1), (1, 4), (0, 'd'), (2, 1), (1, 4)]
    
    def testToData(self):
        result = fo.build_oracle(self.seq1, 'f')
        self.assertEqual(result.data[1:], self.seq1)
        result = fo.build_oracle(self.seq2, 'f')
        self.assertEqual(result.data[1:], self.seq2)

    def testToLrs(self):
        result = fo.build_oracle(self.seq1, 'f')
        self.assertEqual(result.lrs, self.lrs1)
        result = fo.build_oracle(self.seq2, 'f')
        self.assertEqual(result.lrs, self.lrs2)

    def testToCompror(self):
        result = fo.build_oracle(self.seq1, 'f')
        result.encode()
        self.assertEqual(result.get_code(), self.code1)
        result = fo.build_oracle(self.seq2, 'f')
        result.encode()
        self.assertEqual(result.get_code(), self.code2)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
