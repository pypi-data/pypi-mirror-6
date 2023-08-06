# -*- coding: utf-8 -*-

"dk.ttcal"

# pylint:disable=R0904
# R0904: Too many public methods
import six
from unittest import TestCase
from .. import ttcal
from datetime import date, timedelta


class TestDay(TestCase):
    "Unit tests for the ttcal.Day class."
    
    def setUp(self):
        "SetUp default data for the tests."
        self.day1 = ttcal.Day(date(2012, 4, 10))
        self.day2 = ttcal.Day(2012, 4, 8)
        self.day3 = ttcal.Day()
        self.today = ttcal.Today()
    
    def test_get_day_name(self):
        "Test of the get_day_name method."
        self.assertEqual(self.day1.get_day_name(2), 'onsdag')
        self.assertEqual(self.day2.get_day_name(2, 3), 'ons')
    
    def test_hash_(self):
        "Test of the __hash__ method."
        # hash(x) truncates the returned value from __hash__ in Python 3..
        #self.assertEqual(hash(self.day1), hash(hash(self.day1)))
        self.assertEqual(hash(self.day1), hash(self.day1))

    def test_unicode_(self):
        "Test of the __unicode__ method."
        self.assertEqual(six.text_type(self.day2), six.u('2012-04-08'))

    def test_datetuple(self):
        "Test of the datetuple method."
        self.assertEqual(self.day2.datetuple(), tuple((2012, 4, 8)))

    def test_add_(self):
        "Test of the __add__ method."
        self.assertEqual(self.day2 + 3, ttcal.Day(2012, 4, 11))
        
    def test_sub_(self):
        "Test of the __sub__ method."
        self.assertEqual(self.day1 - 5, ttcal.Day(2012, 4, 5))
        
    def test_day_name(self):
        "Test of the day_name property."
        self.assertEqual(self.day1.dayname, 'tirsdag')
        self.assertEqual(self.day2.dayname, u'søndag')

    def test_code(self):
        "Test of the code property."
        self.assertEqual(self.day1.code, 'U')
        
    def test_weeknum(self):
        "Test of the weeknum property."
        self.assertEqual(self.day1.weeknum, 15)
        
    def test_isoyear(self):
        "Test of the isoyear property."
        self.assertEqual(self.day1.isoyear, 2012)
        
    def test_week(self):
        "Test of the week property."
        week = ttcal.Week.weeknum(15, 2012)
        self.assertEqual(self.day1.week, week)
        
    def test_Month(self):
        "Test of the Month property."
        month = ttcal.Month(2012, 4)
        self.assertEqual(self.day1.Month, month)

    def test_Year(self):
        "Test of the Year property."
        year = ttcal.Year(2012)
        self.assertEqual(self.day1.Year, year)

    def test_display(self):
        "Test of the display property."
        #self.assertEqual(self.day3.display, 'today month')
        self.assertTrue('today' in self.day3.display)
        self.assertTrue('month' in self.day3.display)

    def test_idtag(self):
        "Test of the idtag property."
        self.assertEqual(self.day1.idtag, 'd2012041004')
        
    def test_today(self):
        "Test of the today property."
        self.assertTrue(self.day3.today)
        self.assertEqual(self.day1.today, False)
        
    def test_weekday(self):
        "Test of the weekday property."        
        self.assertTrue(self.day1.weekday)
        self.assertNotEqual(self.day2.weekday, True)  # Does not return False
        
    def test_weekend(self):
        "Test of the weekend property."
        self.assertTrue(self.day2.weekend)
        self.assertNotEqual(self.day1.weekend, True)  # Does not return False
        
    def test_in_month(self):
        "Test of the in_month property."
        self.assertTrue(self.day3.in_month)
        
    def test_compare(self):
        "Test the compare method."
        self.assertEqual(self.day1.compare(self.day2), 'month')
        
    def test_compare_specific(self):
        "Test the methods in the CompareMixin class."
        self.assertTrue(self.day1 > self.day2)
        self.assertFalse(self.day1 < self.day2)
        self.assertFalse(self.day1 <= self.day2)
        self.assertTrue(self.day1 >= self.day2)
        self.assertFalse(self.day1 == self.day2)
        self.assertTrue(self.day1 != self.day2)
        
    def test_format(self):
        "Test the format method."
        self.assertEqual(self.day1.format('y-m-d'), '12-04-10')
        self.assertEqual(self.day1.format('Y-W'), '2012-15')
        self.assertEqual(self.day1.format('b'), 'apr')
        self.assertEqual(self.day1.format('w'), '1')
        self.assertEqual(self.day1.format('D-n'), 'tir-4')
        self.assertEqual(self.day1.format('z'), '100')
        self.assertEqual(self.day1.format(), u'Apr 10, 2012')
        
    def test_from_idtag(self):
        "Test the from_idtag method."
        self.assertEqual(ttcal.Day.from_idtag('d2012041004'), self.day1)
        
    def test_parse(self):
        "Test the parse method."
        self.assertEqual(self.day1.parse('04/08/2011'), ttcal.Day(2011, 8, 4))
        self.assertEqual(self.day1.parse('2012-04-06'), ttcal.Day(2012, 4, 6))
        self.assertEqual(self.day1.parse('2012-4-6'), ttcal.Day(2012, 4, 6))
        self.assertEqual(self.day1.parse('20130619'), ttcal.Day(2013, 6, 19))
        self.assertEqual(self.day1.parse('12.11.2013'), ttcal.Day(2013, 11, 12))
        self.assertEqual(self.day1.parse('12.10.13'), ttcal.Day(2013, 10, 12))

        self.assertRaises(ValueError, self.day1.parse, '12.10.11')
        self.assertRaises(ValueError, self.day1.parse, '21/13/2011')


class TestDays(TestCase):
    "Unit tests for the ttcal.Days class."
    
    def setUp(self):
        "SetUp default data for the tests."
        self.days = ttcal.Days(date(2012, 1, 1), date(2012, 1, 10))

    def test_first(self):
        "Test the first property."
        first = self.days.first
        self.assertEqual([first.year, first.month, first.day], [2012, 1, 1])
        
    def test_middle(self):
        "Test the middle property."
        middle = self.days.middle
        self.assertEqual([middle.year, middle.month, middle.day], [2012, 1, 5])

    def test_last(self):
        "Test the last property."
        last = self.days.last
        self.assertEqual([last.year, last.month, last.day], [2012, 1, 10])

    def test_range(self):
        "The the range method defined in the RangeMixin class."
        res = [ttcal.Day(2012, 1, 1), ttcal.Day(2012, 1, 2),
               ttcal.Day(2012, 1, 3), ttcal.Day(2012, 1, 4),
               ttcal.Day(2012, 1, 5), ttcal.Day(2012, 1, 6),
               ttcal.Day(2012, 1, 7), ttcal.Day(2012, 1, 8),
               ttcal.Day(2012, 1, 9), ttcal.Day(2012, 1, 10)]
        self.assertEqual(self.days.range(), res)


class TestWeek(TestCase):
    "Unit tests for the ttcal.Week class."
    
    def setUp(self):
        "SetUp default data for the tests."
        self.week1 = ttcal.Week.weeknum(4, 2012)
        self.week2 = ttcal.Week.weeknum(1)
        self.week3 = ttcal.Week.weeknum(52, 2012)
        self.week4 = ttcal.Week.weeknum(4, 2012)
        
    def test_idtag(self):
        "Test the idtag method."
        currentyear = date.today().year
        self.assertEqual(self.week1.idtag(), 'w20124')
        self.assertEqual(self.week2.idtag(), 'w%s1' % currentyear)
        self.assertEqual(self.week3.idtag(), 'w201252')
            
    def test_datetuple(self):
        "Test the datetuple method."
        self.assertEqual(self.week1.datetuple(), tuple((2012, 1, 23)))
        
    def test_str_(self):
        "Test the __str__ method."
        self.assertEqual(str(self.week1), 'Uke 4 (2012)')
        self.assertEqual(str(self.week3), 'Uke 52 (2012)')

    def test_eq_(self):
        "Test the __eq__ method defined in Week."
        self.assertFalse(self.week1 == self.week2)
        self.assertTrue(self.week1 == self.week4)
        
    def test_from_idtag(self):
        "Test the from_idtag method."
        self.assertEqual(ttcal.Week.from_idtag('w20124'), self.week1)


class TestWeeks(TestCase):
    "Unit tests for the ttcal.Weeks class."
    
    def setUp(self):
        "SetUp default data for the tests."
        self.weeks = ttcal.Weeks(5, 10)  # 5, 6, 7, 8, 9, 10 (n=6)
        self.first = self.weeks.first
        self.last = self.weeks.last
        
    def test_first(self):
        "Test the first property."
        self.assertEqual(self.weeks.first, self.last - 7 * 6 + 1)
    
    def test_last(self):
        "Test the last property."
        self.assertEqual(self.weeks.last, self.first + 7 * 6 - 1)
    
    def test_datetuple(self):
        "Test the datetuple method."
        self.assertEqual(self.weeks.datetuple(), self.first.datetuple())


class TestMonth(TestCase):
    "Unit tests for the ttcal.Month class."
    
    def setUp(self):
        "SetUp initial data used by all tests in this case."
        self.month1 = ttcal.Month(2012, 4)
        self.month2 = ttcal.Month(year=2012, month=10)
        self.month3 = ttcal.Month(date=date(2012, 7, 10))
        # Cannot only specify month, must have year as well.
        self.assertRaises(AssertionError, ttcal.Month, month=10)

    def test_parse(self):
        "ttcal.Month.parse(txt)"
        assert ttcal.Month.parse('2012-04') == self.month1
        assert ttcal.Month.parse('2012-4') == self.month1
        assert ttcal.Month.parse('2012-09') == ttcal.Month(2012, 9)
        
    def test_from_idtag(self):
        "Test the from_idtag method."
        self.assertEqual(ttcal.Month.from_idtag('m201204'), self.month1)
        
    def test_from_date(self):
        "Test the from_date method."
        self.assertEqual(ttcal.Month.from_date(date(2012, 7, 10)), self.month3)
        self.assertEqual(ttcal.Month.from_date(date(2012, 10, 20)), self.month2)
    
    def test_Year(self):
        "Test the Year method."
        self.assertEqual(self.month1.Year, ttcal.Year(2012))
        
    def test_eq_(self):
        "Test the __eq__ method."
        self.assertTrue(self.month1 == date(2012, 4, 5))
        self.assertFalse(self.month2 == self.month1)
        
    def test_len(self):
        "Test the __len__ method."
        self.assertEqual(len(self.month1), 30)
        
    def test_numdays(self):
        "Test the numdays method."
        self.assertEqual(self.month2.numdays(), 31)
        
    def test_add_(self):
        "Test the __add__ method."
        self.assertEqual(self.month1 + 3, ttcal.Month(2012, 7))
        
    def test_sub_(self):
        "Test the __sub__ method."
        self.assertEqual(self.month1 - 3, ttcal.Month(2012, 1))
        
    def test_dayiter(self):
        "Test the dayiter method."
        res = [ttcal.Day(2012, 6, 25), ttcal.Day(2012, 6, 26),
               ttcal.Day(2012, 6, 27)]
        days = []
        for i, day in enumerate(self.month3.dayiter()):
            days.append(day)
            if i == 2:
                break
        self.assertEqual(days, res)
        
    def test_days(self):
        "Test the days method."
        res = [ttcal.Day(2012, 7, 1), ttcal.Day(2012, 7, 2),
               ttcal.Day(2012, 7, 3)]
        self.assertEqual(self.month3.days()[:3], res)
        
    def test_idtag(self):
        "Test the idtag method."
        self.assertEqual(self.month3.idtag(), 'm20127')
        
    def test_daycount(self):
        "Test the daycount property."
        self.assertEqual(self.month3.daycount, 31)
        
    def test_marked_days(self):
        "Test the mark method."
        res = [ttcal.Day(2012, 10, 3), ttcal.Day(2012, 10, 10)]
        self.month2.mark(ttcal.Day(2012, 10, 10))
        self.month2.mark(ttcal.Day(2012, 10, 3))
        days = []
        for day in self.month2.marked_days():
            days.append(day)
        self.assertEqual(days, res)
        
    def test_format(self):
        "Test the format method."
        self.assertEqual(self.month1.format(), 'April, 2012')
        self.assertEqual(self.month1.format('F-Y'), 'April-2012')
        self.assertEqual(self.month1.format('n y'), '4 12')
        self.assertEqual(self.month1.format('m'), '04')
        self.assertEqual(self.month1.format('b'), 'apr')
        self.assertEqual(self.month1.format('M'), 'Apr')


class TestYear(TestCase):
    "Unit tests for the ttcal.Year class."
    
    def setUp(self):
        "SetUp initial data used by all tests in this case."
        self.year1 = ttcal.Year(2005)
        self.year2 = ttcal.Year()
        self.year3 = ttcal.Year(2025)
        
    def test_from_idtag(self):
        "Test of the from_idtag method."
        self.assertEqual(self.year1.from_idtag('y2005'), self.year1)

    def test_idtag(self):
        "Test of the idtag method."
        self.assertEqual(self.year3.idtag(), 'y2025')
    
    def test_add_(self):
        "Test of the __add__ method."
        self.assertEqual(self.year1 + 5, ttcal.Year(2010))
        
    def test_sub_(self):
        "Test of the __sub__ method."
        self.assertEqual(self.year1 - 3, ttcal.Year(2002))
        
    def test_prev(self):
        "Test of the prev method."
        self.assertEqual(self.year1.prev(), ttcal.Year(2004))
    
    def test_next(self):
        "Test of the next method."
        self.assertEqual(self.year1.next(), ttcal.Year(2006))
        
    def test_periods(self):
        "Test of periods using misc methods and properties."
        first_half = [ttcal.Month(2005, 1), ttcal.Month(2005, 2),
                      ttcal.Month(2005, 3), ttcal.Month(2005, 4),
                      ttcal.Month(2005, 5), ttcal.Month(2005, 6)]
        Q3 = [ttcal.Month(2005, 7), ttcal.Month(2005, 8), ttcal.Month(2005, 9)]
        self.assertEqual(self.year1.H1, first_half)
        self.assertEqual(self.year1.Q3, Q3)
        
        self.assert_(self.year1.halves())
        self.assert_(self.year1.quarters())
        self.assert_(self.year1.january)
        self.assert_(self.year1.february)
        self.assert_(self.year1.march)
        self.assert_(self.year1.april)
        self.assert_(self.year1.may)
        self.assert_(self.year1.june)
        self.assert_(self.year1.july)
        self.assert_(self.year1.august)
        self.assert_(self.year1.september)
        self.assert_(self.year1.october)
        self.assert_(self.year1.november)
        self.assert_(self.year1.december)
        
    def test_mark_period(self):
        "Test the mark_period method."
        res = [ttcal.Day(2025, 3, 1), ttcal.Day(2025, 3, 2),
               ttcal.Day(2025, 3, 3)]
        self.year3.mark_period(self.year3.march)
        days = []
        for i, day in enumerate(self.year3.marked_days()):
            days.append(day)
            if i == 2:
                break
        self.assertEqual(days, res)
        
    def test_eq_(self):
        "Test the __eq__ method."
        self.assertTrue(self.year2 == ttcal.Year(date.today().year))
        self.assertFalse(self.year1 == self.year3)
            

class TestDuration(TestCase):
    "Unit tests for the ttcal.Duration class."
    
    def setUp(self):
        "SetUp initial data used by all tests in this case."
        self.duration1 = ttcal.Duration(days=1, hours=3, minutes=14, seconds=20)
        self.duration2 = ttcal.Duration(days=0, hours=1, minutes=10, seconds=0)
        self.duration3 = ttcal.Duration(days=0, hours=0, minutes=70, seconds=0)
        self.duration4 = ttcal.Duration(timedelta(minutes=70))
        
    def test_duration_tuple(self):
        "Test of the duration_tuple method."
        self.assertEqual(self.duration1.duration_tuple(),
                         tuple(('', 27, 14, 20)))
        
    def test_str_(self):
        "Test of the __str__ method."
        self.assertEqual(str(self.duration2), '1:10:00')
        self.assertEqual(str(self.duration3), '1:10:00')
        
    def test_parse(self):
        "Test of the parse method."
        self.assertEqual(self.duration1.parse('01:10:00'), self.duration2)
        
    def test_add_(self):
        "Test of the __add__ method."
        self.assertEqual(self.duration2 + self.duration3,
                         ttcal.Duration(hours=2, minutes=20))
        
    def test_sub_(self):
        "Test of the __sub__ method."
        self.assertEqual(self.duration1 - self.duration2,
                         ttcal.Duration(days=1, hours=2, minutes=4, seconds=20))
        
    def test_mul_(self):
        "Test of the __mul__ method."
        self.assertEqual(self.duration2 * 3,
                         ttcal.Duration(hours=3, minutes=30))
    
    def test_div_(self):
        "Test of the __div__ method."
        self.assertEqual(self.duration2 / 2,
                         ttcal.Duration(minutes=35))
        
        # Unable to catch the error.
        # self.assertRaises(ZeroDivisionError, self.duration2 / 0)
