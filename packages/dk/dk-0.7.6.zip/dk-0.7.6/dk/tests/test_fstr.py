# -*- coding: utf-8 -*-

"core.fstr"

# pylint:disable=R0904
# R0904: Too many public methods

from unittest import TestCase
from ..fstr import fstr


class TestFstr(TestCase):
    "Unit test of the fstr module"
    
    def test_split(self):
        "Test of the split method."
        r = fstr('D2008022002')
        
        self.assertEqual(
            r.split(1, 5, 7, 9), ['D', '2008', '02', '20', '02'])
        self.assertEqual(
            fstr('0123456789').split(), ['0123456789'])
        self.assertEqual(
            fstr('0123456789').split(5), ['01234', '56789'])
        self.assertEqual(
            fstr('0123456789').split(3, 6), ['012', '345', '6789'])
        self.assertEqual(
            fstr('0123456789').split(2, 4, 6), ['01', '23', '45', '6789'])
