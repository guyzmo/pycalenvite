#!/usr/bin/env python

#from tempfile import TemporaryDirectory

#from testfixtures import Replace, ShouldRaise, compare
#from testfixtures.popen import MockPopen

import pytest

from datetime import datetime as dt, timedelta as td

from calenvite.calenvite import Calendar, Event, Timeline

from pprint import pprint


class TestCalendar:
    def setup_method(self, method):
        self.calendar = Calendar()

    def teardown_method(self, method):
        pass

    def test__reduce_overlaps__disjoint_events(self):
        cal = Calendar()
        cal.events = set()
        cal.uid = Calendar.EventUid()
        # recursion #1
        events = cal._reduce_overlaps(
                cal.events,
                Event(name='Test #1', uid='a', begin=dt(2016, 6, 10, 20, 00), duration=td(minutes=10)),
                )
        pprint(events)
        assert events == {
                Event(name=None, uid='0', begin=dt(2016, 6, 10, 20, 00), duration=td(minutes=10)),
                }
        cal.events = events
        # recursion #2
        events = cal._reduce_overlaps(
                cal.events,
                Event(name='Test #2', uid='b', begin=dt(2016, 6, 10, 20, 20), duration=td(minutes=10))
                )
        pprint(events)
        assert events == {
                Event(name=None, uid='0', begin=dt(2016, 6, 10, 20, 00), duration=td(minutes=10)),
                Event(name=None, uid='1', begin=dt(2016, 6, 10, 20, 20), duration=td(minutes=10)),
                }

    def test__reduce_overlaps__intersecting_events(self):
        cal = Calendar()
        cal.events = set()
        cal.uid = Calendar.EventUid()
        # recursion #1
        events = cal._reduce_overlaps(
                cal.events,
                Event(name='Test #1', uid='a', begin=dt(2016, 6, 10, 20, 00), duration=td(minutes=40)),
                )
        pprint(events)
        assert events == {
                Event(name=None, uid='0', begin=dt(2016, 6, 10, 20, 00), duration=td(minutes=40)),
                }
        cal.events = events
        # recursion #2
        events = cal._reduce_overlaps(
                cal.events,
                Event(name='Test #2', uid='b', begin=dt(2016, 6, 10, 20, 20), duration=td(minutes=50))
                )
        pprint(events)
        assert events == {
                Event(name=None, uid='1', begin=dt(2016, 6, 10, 20, 00), duration=td(minutes=70)),
                }

    def test__reduce_overlaps__inclusing_events__big_first(self):
        cal = Calendar()
        cal.events = set()
        cal.uid = Calendar.EventUid()
        # recursion #1
        events = cal._reduce_overlaps(
                cal.events,
                Event(name='Test #1', uid='a', begin=dt(2016, 6, 10, 20, 00), duration=td(minutes=60)),
                )
        pprint(events)
        assert events == {
                Event(name=None, uid='0', begin=dt(2016, 6, 10, 20, 00), duration=td(minutes=60)),
                }
        cal.events = events
        # recursion #2
        events = cal._reduce_overlaps(
                cal.events,
                Event(name='Test #2', uid='b', begin=dt(2016, 6, 10, 20, 20), duration=td(minutes=30))
                )
        pprint(events)
        assert events == {
                Event(name=None, uid='1', begin=dt(2016, 6, 10, 20, 00), duration=td(minutes=60)),
                }

    def test__reduce_overlaps__inclusing_events__small_first(self):
        cal = Calendar()
        cal.events = set()
        cal.uid = Calendar.EventUid()
        # recursion #1
        events = cal._reduce_overlaps(
                cal.events,
                Event(name='Test #1', uid='b', begin=dt(2016, 6, 10, 20, 20), duration=td(minutes=30))
                )
        pprint(events)
        assert events == {
                Event(name=None, uid='0', begin=dt(2016, 6, 10, 20, 20), duration=td(minutes=30)),
                }
        cal.events = events
        # recursion #2
        events = cal._reduce_overlaps(
                cal.events,
                Event(name='Test #2', uid='a', begin=dt(2016, 6, 10, 20, 00), duration=td(minutes=60)),
                )
        pprint(events)
        assert events == {
                Event(name=None, uid='1', begin=dt(2016, 6, 10, 20, 00), duration=td(minutes=60)),
                }

    def test_merge__single_calendar__disjoint(self):
        cal = Calendar()
        cal.events = {
                Event(uid='t0', name='Test #1', begin=dt(2016, 6, 10, 20, 10), duration=td(minutes=20)),
                Event(uid='t1', name='Test #2', begin=dt(2016, 6, 10, 20, 50), duration=td(minutes=20)),
                Event(uid='t2', name='Test #3', begin=dt(2016, 6, 10, 21, 30), duration=td(minutes=30)),
                }
        self.calendar.merge(cal)
        pprint(self.calendar.events)
        assert self.calendar.events == {
                Event(name='Test #1', uid='0', begin=dt(2016, 6, 10, 20, 10), duration=td(minutes=20)),
                Event(name='Test #2', uid='1', begin=dt(2016, 6, 10, 20, 50), duration=td(minutes=20)),
                Event(name='Test #3', uid='2', begin=dt(2016, 6, 10, 21, 30), duration=td(minutes=30)),
                }

    def test_merge__single_calendar___inclusion___two_events(self):
        cal = Calendar()
        cal.events = {
                Event(name='Test #1', begin=dt(2016, 6, 10, 20, 00), duration=td(minutes=60)),
                Event(name='Test #2', begin=dt(2016, 6, 10, 20, 20), duration=td(minutes=20)),
                }
        self.calendar.merge(cal)
        pprint(self.calendar.events)
        assert self.calendar.events == {
                Event(name=None, uid='0', begin=dt(2016, 6, 10, 20, 00), duration=td(minutes=60)),
                }

    def test_merge__single_calendar___inclusion___two_events_rev(self):
        # check the other way around
        cal = Calendar()
        cal.events = {
                Event(name='Test #1', begin=dt(2016, 6, 10, 20, 20), duration=td(minutes=20)),
                Event(name='Test #2', begin=dt(2016, 6, 10, 20, 00), duration=td(minutes=60)),
                }
        self.calendar.merge(cal)
        pprint(self.calendar.events)
        assert self.calendar.events == {
                Event(name=None, uid='0', begin=dt(2016, 6, 10, 20, 00), duration=td(minutes=60)),
                }

    def test_merge__single_calendar___inclusion_three_events__1(self):
        cal = Calendar()
        cal.events = {
                Event(uid='t0', name='Test #1', begin=dt(2016, 6, 10, 20, 00), duration=td(minutes=60)),
                Event(uid='t1', name='Test #2', begin=dt(2016, 6, 10, 20, 20), duration=td(minutes=20)),
                Event(uid='t2', name='Test #3', begin=dt(2016, 6, 10, 20, 30), duration=td(minutes=20)),
                }
        self.calendar.merge(cal)
        pprint(self.calendar.events)
        assert self.calendar.events == {
                Event(name=None, uid='0', begin=dt(2016, 6, 10, 20, 00), duration=td(minutes=60)),
                }

    def test_merge__single_calendar___inclusion_three_events__2(self):
        # big one in the middle
        cal = Calendar()
        cal.events = {
                Event(name='Test #1', begin=dt(2016, 6, 10, 20, 20), duration=td(minutes=20)),
                Event(name='Test #2', begin=dt(2016, 6, 10, 20, 00), duration=td(minutes=60)),
                Event(name='Test #3', begin=dt(2016, 6, 10, 20, 30), duration=td(minutes=20)),
                }
        self.calendar.merge(cal)
        pprint(self.calendar.events)
        assert self.calendar.events == {
                Event(name=None, uid='0', begin=dt(2016, 6, 10, 20, 00), duration=td(minutes=60)),
                }

    def test_merge__single_calendar___inclusion_three_events__3(self):
        # big one at the end
        cal = Calendar()
        cal.events = {
                Event(name='Test #1', begin=dt(2016, 6, 10, 20, 20), duration=td(minutes=20)),
                Event(name='Test #2', begin=dt(2016, 6, 10, 20, 30), duration=td(minutes=20)),
                Event(name='Test #3', begin=dt(2016, 6, 10, 20, 00), duration=td(minutes=60)),
                }
        self.calendar.merge(cal)
        pprint(self.calendar.events)
        assert self.calendar.events == {
                Event(name=None, uid='0', begin=dt(2016, 6, 10, 20, 00), duration=td(minutes=60)),
                }


    def test_merge_____two_calendars__disjoint(self):
        # first calendar
        cal = Calendar()
        cal.events = {
                Event(name='Test #1', begin=dt(2016, 6, 10, 20, 10), duration=td(minutes=20)),
                Event(name='Test #2', begin=dt(2016, 6, 10, 20, 50), duration=td(minutes=20)),
                Event(name='Test #3', begin=dt(2016, 6, 10, 21, 30), duration=td(minutes=30)),
                }
        self.calendar.merge(cal)
        pprint(self.calendar.events)
        # second calendar
        cal = Calendar()
        cal.events = {
                Event(name='Test #4', uid='d', begin=dt(2016, 6, 11, 12, 10), duration=td(minutes=20)),
                Event(name='Test #5', uid='e', begin=dt(2016, 6, 11, 12, 40), duration=td(minutes=20)),
                Event(name='Test #6', uid='f', begin=dt(2016, 6, 11, 13, 30), duration=td(minutes=30)),
                }
        self.calendar.merge(cal)
        pprint(self.calendar.events)
        assert self.calendar.events == {
                Event(name='Test #1', uid='0', begin=dt(2016, 6, 10, 20, 10), duration=td(minutes=20)),
                Event(name='Test #2', uid='1', begin=dt(2016, 6, 10, 20, 50), duration=td(minutes=20)),
                Event(name='Test #3', uid='2', begin=dt(2016, 6, 10, 21, 30), duration=td(minutes=30)),
                Event(name='Test #4', uid='3', begin=dt(2016, 6, 10, 12, 10), duration=td(minutes=20)),
                Event(name='Test #5', uid='4', begin=dt(2016, 6, 10, 12, 40), duration=td(minutes=20)),
                Event(name='Test #6', uid='5', begin=dt(2016, 6, 10, 12, 30), duration=td(minutes=30)),
                }

    def test_merge__single_calendar___overlapping_two_events(self):
        '''
        testing overlapping 2 events:

            <20:00 → 20:40> + <20:20 → 21:00>
            = <20:00 → 20:40>

        '''
        cal = Calendar()
        cal.events = {
                Event(name='Test #1', begin=dt(2016, 6, 10, 20, 00), duration=td(minutes=40)),
                Event(name='Test #2', begin=dt(2016, 6, 10, 20, 20), duration=td(minutes=40)),
                }
        self.calendar.merge(cal)
        assert len(self.calendar.events) == 1
        assert self.calendar.events == {
                Event(name=None, uid='0', begin=dt(2016, 6, 10, 20, 00), duration=td(minutes=60)),
                }

    def test_merge__single_calendar___overlapping_three_events(self):
        '''
        testing overlapping 3 events:

            <20:00→20:20> <20:10→20:50> <20:40→21:00>
            = <20:00→21:00>

        '''
        cal = Calendar()
        cal.events = {
                Event(uid='t1', name='Test #1', begin=dt(2016, 6, 10, 20, 00), duration=td(minutes=20)),
                Event(uid='t2', name='Test #2', begin=dt(2016, 6, 10, 20, 10), duration=td(minutes=40)),
                Event(uid='t3', name='Test #3', begin=dt(2016, 6, 10, 20, 40), duration=td(minutes=20)),
                }
        self.calendar.merge(cal)
        assert len(self.calendar.events) == 1
        res = Calendar()
        cal.events = {
                Event(name=None, uid='0', begin=dt(2016, 6, 10, 20, 00), duration=td(minutes=60)),
                }
        assert self.calendar.events == cal.events

    def test_merge_____two_calendars__overlapping_two_events(self):
        '''
        testing overlapping 2 events (each one in a different calendar):

            <20:00 → 20:40> + <20:20 → 21:00>
            = <20:00 → 20:40>

        '''
        cal = Calendar()
        cal.events = {
                Event(name='Test #1', begin=dt(2016, 6, 10, 20, 00), duration=td(minutes=40)),
                }
        self.calendar.merge(cal)
        assert len(self.calendar.events) == 1
        cal = Calendar()
        cal.events = {
                Event(name='Test #2', begin=dt(2016, 6, 10, 20, 20), duration=td(minutes=40)),
                }
        self.calendar.merge(cal)
        assert len(self.calendar.events) == 1
        assert self.calendar.events == {
                Event(name=None, uid='0', begin=dt(2016, 6, 10, 20, 00), duration=td(minutes=60)),
                }

    def test_merge___three_calendars__overlapping_three_events(self):
        '''
        testing overlapping 3 events (each one in a different calendar):

            <20:00→20:20> <20:10→20:50> <20:40→21:00>
            = <20:00→21:00>

        '''
        cal = Calendar()
        cal.events = {
                Event(name='Test #1', begin=dt(2016, 6, 10, 20, 00), duration=td(minutes=20)),
                }
        self.calendar.merge(cal)
        assert len(self.calendar.events) == 1
        cal = Calendar()
        cal.events = {
                Event(name='Test #2', begin=dt(2016, 6, 10, 20, 10), duration=td(minutes=40)),
                }
        self.calendar.merge(cal)
        assert len(self.calendar.events) == 1
        cal = Calendar()
        cal.events = {
                Event(name='Test #3', begin=dt(2016, 6, 10, 20, 40), duration=td(minutes=20)),
                }
        self.calendar.merge(cal)
        assert len(self.calendar.events) == 1
        res = Calendar()
        cal.events = {
                Event(name=None, uid='0', begin=dt(2016, 6, 10, 20, 00), duration=td(minutes=60)),
                }
        assert self.calendar.events == cal.events

    def test_has_slot(self):
        self.calendar.events = {
                Event(name=None, uid='0', begin=dt(2016, 6, 10, 20, 00), duration=td(minutes=20)),
                Event(name=None, uid='1', begin=dt(2016, 6, 10, 21, 00), duration=td(minutes=20)),
                Event(name=None, uid='2', begin=dt(2016, 6, 10, 22, 00), duration=td(minutes=180)),
                }
        assert not self.calendar.has_slot(
                Event(name='Test #1', uid='a', begin=dt(2016, 6, 10, 19, 30), duration=td(minutes=60)),
                )
        assert not self.calendar.has_slot(
                Event(name='Test #1', uid='a', begin=dt(2016, 6, 10, 20, 30), duration=td(minutes=60)),
                )
        assert not self.calendar.has_slot(
                Event(name='Test #1', uid='a', begin=dt(2016, 6, 10, 23, 00), duration=td(minutes=60)),
                )
        assert self.calendar.has_slot(
                Event(name='Test #1', uid='a', begin=dt(2016, 6, 10, 19, 30), duration=td(minutes=10)),
                )
        assert self.calendar.has_slot(
                Event(name='Test #1', uid='a', begin=dt(2016, 6, 10, 20, 30), duration=td(minutes=10)),
                )
        assert self.calendar.has_slot(
                Event(name='Test #1', uid='a', begin=dt(2016, 6, 10, 21, 21), duration=td(minutes=10)),
                )
        assert self.calendar.has_slot(
                Event(name='Test #1', uid='a', begin=dt(2016, 6, 11,  1,  1), duration=td(minutes=10)),
                )

####################################################################################

from calenvite.calenvite import Calenvite
from dateutil.parser import parse as dp

class TestCalenvite:
    def setup_method(self, method):
        self.cal = Calenvite()

    def test__generate_uuid(self):
        '''Makes sure that UUID really is unique in a million tries'''
        uuid = self.cal._generate_uuid()
        assert uuid not in self.cal._pending
        self.cal._pending[uuid] = None

    def check_first(self):
        tl = list(self.cal._calendar_soup.timeline)
        assert tl[ 0].begin.datetime == dp('2015-01-01T00:00:00+00:00') ; assert tl[ 0].end.datetime == dp('2015-01-03T00:00:00+00:00') ; assert tl[ 0].all_day == True
        assert tl[ 1].begin.datetime == dp('2015-04-03T00:00:00+00:00') ; assert tl[ 1].end.datetime == dp('2015-04-08T00:00:00+00:00') ; assert tl[ 1].all_day == False
        assert tl[ 2].begin.datetime == dp('2015-05-01T00:00:00+00:00') ; assert tl[ 2].end.datetime == dp('2015-05-03T00:00:00+00:00') ; assert tl[ 2].all_day == True
        assert tl[ 3].begin.datetime == dp('2015-05-08T00:00:00+00:00') ; assert tl[ 3].end.datetime == dp('2015-05-10T00:00:00+00:00') ; assert tl[ 3].all_day == True
        assert tl[ 4].begin.datetime == dp('2015-05-14T00:00:00+00:00') ; assert tl[ 4].end.datetime == dp('2015-05-16T00:00:00+00:00') ; assert tl[ 4].all_day == True
        assert tl[ 5].begin.datetime == dp('2015-05-24T00:00:00+00:00') ; assert tl[ 5].end.datetime == dp('2015-05-27T00:00:00+00:00') ; assert tl[ 5].all_day == False
        assert tl[ 6].begin.datetime == dp('2015-07-14T00:00:00+00:00') ; assert tl[ 6].end.datetime == dp('2015-07-16T00:00:00+00:00') ; assert tl[ 6].all_day == True
        assert tl[ 7].begin.datetime == dp('2015-08-15T00:00:00+00:00') ; assert tl[ 7].end.datetime == dp('2015-08-17T00:00:00+00:00') ; assert tl[ 7].all_day == True
        assert tl[ 8].begin.datetime == dp('2015-11-01T00:00:00+00:00') ; assert tl[ 8].end.datetime == dp('2015-11-03T00:00:00+00:00') ; assert tl[ 8].all_day == True
        assert tl[ 9].begin.datetime == dp('2015-11-11T00:00:00+00:00') ; assert tl[ 9].end.datetime == dp('2015-11-13T00:00:00+00:00') ; assert tl[ 9].all_day == True
        assert tl[10].begin.datetime == dp('2015-12-25T00:00:00+00:00') ; assert tl[10].end.datetime == dp('2015-12-27T00:00:00+00:00') ; assert tl[10].all_day == True
        assert tl[11].begin.datetime == dp('2015-12-31T00:00:00+00:00') ; assert tl[11].end.datetime == dp('2016-01-03T00:00:00+00:00') ; assert tl[11].all_day == False
        assert tl[12].begin.datetime == dp('2016-03-25T00:00:00+00:00') ; assert tl[12].end.datetime == dp('2016-03-30T00:00:00+00:00') ; assert tl[12].all_day == False
        assert tl[13].begin.datetime == dp('2016-05-01T00:00:00+00:00') ; assert tl[13].end.datetime == dp('2016-05-03T00:00:00+00:00') ; assert tl[13].all_day == True
        assert tl[14].begin.datetime == dp('2016-05-05T00:00:00+00:00') ; assert tl[14].end.datetime == dp('2016-05-07T00:00:00+00:00') ; assert tl[14].all_day == True
        assert tl[15].begin.datetime == dp('2016-05-08T00:00:00+00:00') ; assert tl[15].end.datetime == dp('2016-05-10T00:00:00+00:00') ; assert tl[15].all_day == True
        assert tl[16].begin.datetime == dp('2016-05-15T00:00:00+00:00') ; assert tl[16].end.datetime == dp('2016-05-18T00:00:00+00:00') ; assert tl[16].all_day == False
        assert tl[17].begin.datetime == dp('2016-07-14T00:00:00+00:00') ; assert tl[17].end.datetime == dp('2016-07-16T00:00:00+00:00') ; assert tl[17].all_day == True
        assert tl[18].begin.datetime == dp('2016-08-15T00:00:00+00:00') ; assert tl[18].end.datetime == dp('2016-08-17T00:00:00+00:00') ; assert tl[18].all_day == True
        assert tl[19].begin.datetime == dp('2016-11-01T00:00:00+00:00') ; assert tl[19].end.datetime == dp('2016-11-03T00:00:00+00:00') ; assert tl[19].all_day == True
        assert tl[20].begin.datetime == dp('2016-11-11T00:00:00+00:00') ; assert tl[20].end.datetime == dp('2016-11-13T00:00:00+00:00') ; assert tl[20].all_day == True
        assert tl[21].begin.datetime == dp('2016-12-25T00:00:00+00:00') ; assert tl[21].end.datetime == dp('2016-12-27T00:00:00+00:00') ; assert tl[21].all_day == True
        assert tl[22].begin.datetime == dp('2016-12-31T00:00:00+00:00') ; assert tl[22].end.datetime == dp('2017-01-02T00:00:00+00:00') ; assert tl[22].all_day == True

    def check_second(self):
        tl = list(self.cal._calendar_soup.timeline)
        assert tl[ 0].begin.datetime == dp('2015-01-01T00:00:00+00:00') ; assert tl[ 0].end.datetime == dp('2015-01-03T00:00:00+00:00') ; assert tl[ 0].all_day == False
        assert tl[ 1].begin.datetime == dp('2015-04-03T00:00:00+00:00') ; assert tl[ 1].end.datetime == dp('2015-04-08T00:00:00+00:00') ; assert tl[ 1].all_day == False
        assert tl[ 2].begin.datetime == dp('2015-05-01T00:00:00+00:00') ; assert tl[ 2].end.datetime == dp('2015-05-03T00:00:00+00:00') ; assert tl[ 2].all_day == True
        assert tl[ 3].begin.datetime == dp('2015-05-04T00:00:00+00:00') ; assert tl[ 3].end.datetime == dp('2015-05-06T00:00:00+00:00') ; assert tl[ 3].all_day == True
        assert tl[ 4].begin.datetime == dp('2015-05-08T00:00:00+00:00') ; assert tl[ 4].end.datetime == dp('2015-05-10T00:00:00+00:00') ; assert tl[ 4].all_day == True
        assert tl[ 5].begin.datetime == dp('2015-05-14T00:00:00+00:00') ; assert tl[ 5].end.datetime == dp('2015-05-16T00:00:00+00:00') ; assert tl[ 5].all_day == True
        assert tl[ 6].begin.datetime == dp('2015-05-24T00:00:00+00:00') ; assert tl[ 6].end.datetime == dp('2015-05-27T00:00:00+00:00') ; assert tl[ 6].all_day == False
        assert tl[ 7].begin.datetime == dp('2015-07-14T00:00:00+00:00') ; assert tl[ 7].end.datetime == dp('2015-07-16T00:00:00+00:00') ; assert tl[ 7].all_day == True
        assert tl[ 8].begin.datetime == dp('2015-08-03T00:00:00+00:00') ; assert tl[ 8].end.datetime == dp('2015-08-05T00:00:00+00:00') ; assert tl[ 8].all_day == True
        assert tl[ 9].begin.datetime == dp('2015-08-15T00:00:00+00:00') ; assert tl[ 9].end.datetime == dp('2015-08-17T00:00:00+00:00') ; assert tl[ 9].all_day == True
        assert tl[10].begin.datetime == dp('2015-08-31T00:00:00+00:00') ; assert tl[10].end.datetime == dp('2015-09-02T00:00:00+00:00') ; assert tl[10].all_day == True
        assert tl[11].begin.datetime == dp('2015-10-31T00:00:00+00:00') ; assert tl[11].end.datetime == dp('2015-11-03T00:00:00+00:00') ; assert tl[11].all_day == False
        assert tl[12].begin.datetime == dp('2015-11-05T00:00:00+00:00') ; assert tl[12].end.datetime == dp('2015-11-07T00:00:00+00:00') ; assert tl[12].all_day == True
        assert tl[13].begin.datetime == dp('2015-11-11T00:00:00+00:00') ; assert tl[13].end.datetime == dp('2015-11-13T00:00:00+00:00') ; assert tl[13].all_day == True
        assert tl[14].begin.datetime == dp('2015-12-25T00:00:00+00:00') ; assert tl[14].end.datetime == dp('2015-12-28T00:00:00+00:00') ; assert tl[14].all_day == False
        assert tl[15].begin.datetime == dp('2015-12-31T00:00:00+00:00') ; assert tl[15].end.datetime == dp('2016-01-03T00:00:00+00:00') ; assert tl[15].all_day == False
        assert tl[16].begin.datetime == dp('2016-03-25T00:00:00+00:00') ; assert tl[16].end.datetime == dp('2016-03-30T00:00:00+00:00') ; assert tl[16].all_day == False
        assert tl[17].begin.datetime == dp('2016-05-01T00:00:00+00:00') ; assert tl[17].end.datetime == dp('2016-05-04T00:00:00+00:00') ; assert tl[17].all_day == False
        assert tl[18].begin.datetime == dp('2016-05-05T00:00:00+00:00') ; assert tl[18].end.datetime == dp('2016-05-07T00:00:00+00:00') ; assert tl[18].all_day == True
        assert tl[19].begin.datetime == dp('2016-05-08T00:00:00+00:00') ; assert tl[19].end.datetime == dp('2016-05-10T00:00:00+00:00') ; assert tl[19].all_day == True
        assert tl[20].begin.datetime == dp('2016-05-15T00:00:00+00:00') ; assert tl[20].end.datetime == dp('2016-05-18T00:00:00+00:00') ; assert tl[20].all_day == False
        assert tl[21].begin.datetime == dp('2016-05-30T00:00:00+00:00') ; assert tl[21].end.datetime == dp('2016-06-01T00:00:00+00:00') ; assert tl[21].all_day == True
        assert tl[22].begin.datetime == dp('2016-07-14T00:00:00+00:00') ; assert tl[22].end.datetime == dp('2016-07-16T00:00:00+00:00') ; assert tl[22].all_day == True
        assert tl[23].begin.datetime == dp('2016-08-01T00:00:00+00:00') ; assert tl[23].end.datetime == dp('2016-08-03T00:00:00+00:00') ; assert tl[23].all_day == True
        assert tl[24].begin.datetime == dp('2016-08-15T00:00:00+00:00') ; assert tl[24].end.datetime == dp('2016-08-17T00:00:00+00:00') ; assert tl[24].all_day == True
        assert tl[25].begin.datetime == dp('2016-08-29T00:00:00+00:00') ; assert tl[25].end.datetime == dp('2016-08-31T00:00:00+00:00') ; assert tl[25].all_day == True
        assert tl[26].begin.datetime == dp('2016-10-31T00:00:00+00:00') ; assert tl[26].end.datetime == dp('2016-11-03T00:00:00+00:00') ; assert tl[26].all_day == False
        assert tl[27].begin.datetime == dp('2016-11-05T00:00:00+00:00') ; assert tl[27].end.datetime == dp('2016-11-07T00:00:00+00:00') ; assert tl[27].all_day == True
        assert tl[28].begin.datetime == dp('2016-11-11T00:00:00+00:00') ; assert tl[28].end.datetime == dp('2016-11-13T00:00:00+00:00') ; assert tl[28].all_day == True
        assert tl[29].begin.datetime == dp('2016-12-25T00:00:00+00:00') ; assert tl[29].end.datetime == dp('2016-12-29T00:00:00+00:00') ; assert tl[29].all_day == False
        assert tl[30].begin.datetime == dp('2016-12-31T00:00:00+00:00') ; assert tl[30].end.datetime == dp('2017-01-02T00:00:00+00:00') ; assert tl[30].all_day == True

    def check_third(self):
        tl = list(self.cal._calendar_soup.timeline)
        assert tl[ 0].begin.datetime == dp('2015-01-01T00:00:00+00:00') ; assert tl[ 0].end.datetime == dp('2015-01-03T00:00:00+00:00') ; assert tl[ 0].all_day == False
        assert tl[ 1].begin.datetime == dp('2015-01-19T00:00:00+00:00') ; assert tl[ 1].end.datetime == dp('2015-01-21T00:00:00+00:00') ; assert tl[ 1].all_day == True
        assert tl[ 2].begin.datetime == dp('2015-02-14T00:00:00+00:00') ; assert tl[ 2].end.datetime == dp('2015-02-18T00:00:00+00:00') ; assert tl[ 2].all_day == False
        assert tl[ 3].begin.datetime == dp('2015-04-03T00:00:00+00:00') ; assert tl[ 3].end.datetime == dp('2015-04-08T00:00:00+00:00') ; assert tl[ 3].all_day == False
        assert tl[ 4].begin.datetime == dp('2015-05-01T00:00:00+00:00') ; assert tl[ 4].end.datetime == dp('2015-05-03T00:00:00+00:00') ; assert tl[ 4].all_day == True
        assert tl[ 5].begin.datetime == dp('2015-05-04T00:00:00+00:00') ; assert tl[ 5].end.datetime == dp('2015-05-06T00:00:00+00:00') ; assert tl[ 5].all_day == True
        assert tl[ 6].begin.datetime == dp('2015-05-08T00:00:00+00:00') ; assert tl[ 6].end.datetime == dp('2015-05-12T00:00:00+00:00') ; assert tl[ 6].all_day == False
        assert tl[ 7].begin.datetime == dp('2015-05-14T00:00:00+00:00') ; assert tl[ 7].end.datetime == dp('2015-05-16T00:00:00+00:00') ; assert tl[ 7].all_day == True
        assert tl[ 8].begin.datetime == dp('2015-05-24T00:00:00+00:00') ; assert tl[ 8].end.datetime == dp('2015-05-27T00:00:00+00:00') ; assert tl[ 8].all_day == False
        assert tl[ 9].begin.datetime == dp('2015-06-21T00:00:00+00:00') ; assert tl[ 9].end.datetime == dp('2015-06-23T00:00:00+00:00') ; assert tl[ 9].all_day == True
        assert tl[10].begin.datetime == dp('2015-07-04T00:00:00+00:00') ; assert tl[10].end.datetime == dp('2015-07-06T00:00:00+00:00') ; assert tl[10].all_day == True
        assert tl[11].begin.datetime == dp('2015-07-14T00:00:00+00:00') ; assert tl[11].end.datetime == dp('2015-07-16T00:00:00+00:00') ; assert tl[11].all_day == True
        assert tl[12].begin.datetime == dp('2015-08-03T00:00:00+00:00') ; assert tl[12].end.datetime == dp('2015-08-05T00:00:00+00:00') ; assert tl[12].all_day == True
        assert tl[13].begin.datetime == dp('2015-08-15T00:00:00+00:00') ; assert tl[13].end.datetime == dp('2015-08-17T00:00:00+00:00') ; assert tl[13].all_day == True
        assert tl[14].begin.datetime == dp('2015-08-31T00:00:00+00:00') ; assert tl[14].end.datetime == dp('2015-09-02T00:00:00+00:00') ; assert tl[14].all_day == True
        assert tl[15].begin.datetime == dp('2015-09-07T00:00:00+00:00') ; assert tl[15].end.datetime == dp('2015-09-09T00:00:00+00:00') ; assert tl[15].all_day == True
        assert tl[16].begin.datetime == dp('2015-10-12T00:00:00+00:00') ; assert tl[16].end.datetime == dp('2015-10-14T00:00:00+00:00') ; assert tl[16].all_day == True
        assert tl[17].begin.datetime == dp('2015-10-31T00:00:00+00:00') ; assert tl[17].end.datetime == dp('2015-11-03T00:00:00+00:00') ; assert tl[17].all_day == False
        assert tl[18].begin.datetime == dp('2015-11-05T00:00:00+00:00') ; assert tl[18].end.datetime == dp('2015-11-07T00:00:00+00:00') ; assert tl[18].all_day == True
        assert tl[19].begin.datetime == dp('2015-11-11T00:00:00+00:00') ; assert tl[19].end.datetime == dp('2015-11-13T00:00:00+00:00') ; assert tl[19].all_day == False
        assert tl[20].begin.datetime == dp('2015-11-26T00:00:00+00:00') ; assert tl[20].end.datetime == dp('2015-11-28T00:00:00+00:00') ; assert tl[20].all_day == True
        assert tl[21].begin.datetime == dp('2015-12-25T00:00:00+00:00') ; assert tl[21].end.datetime == dp('2015-12-28T00:00:00+00:00') ; assert tl[21].all_day == False
        assert tl[22].begin.datetime == dp('2015-12-31T00:00:00+00:00') ; assert tl[22].end.datetime == dp('2016-01-03T00:00:00+00:00') ; assert tl[22].all_day == False
        assert tl[23].begin.datetime == dp('2016-01-18T00:00:00+00:00') ; assert tl[23].end.datetime == dp('2016-01-20T00:00:00+00:00') ; assert tl[23].all_day == True
        assert tl[24].begin.datetime == dp('2016-02-14T00:00:00+00:00') ; assert tl[24].end.datetime == dp('2016-02-17T00:00:00+00:00') ; assert tl[24].all_day == False
        assert tl[25].begin.datetime == dp('2016-03-25T00:00:00+00:00') ; assert tl[25].end.datetime == dp('2016-03-30T00:00:00+00:00') ; assert tl[25].all_day == False
        assert tl[26].begin.datetime == dp('2016-05-01T00:00:00+00:00') ; assert tl[26].end.datetime == dp('2016-05-04T00:00:00+00:00') ; assert tl[26].all_day == False
        assert tl[27].begin.datetime == dp('2016-05-05T00:00:00+00:00') ; assert tl[27].end.datetime == dp('2016-05-07T00:00:00+00:00') ; assert tl[27].all_day == True
        assert tl[28].begin.datetime == dp('2016-05-08T00:00:00+00:00') ; assert tl[28].end.datetime == dp('2016-05-10T00:00:00+00:00') ; assert tl[28].all_day == False
        assert tl[29].begin.datetime == dp('2016-05-15T00:00:00+00:00') ; assert tl[29].end.datetime == dp('2016-05-18T00:00:00+00:00') ; assert tl[29].all_day == False
        assert tl[30].begin.datetime == dp('2016-05-30T00:00:00+00:00') ; assert tl[30].end.datetime == dp('2016-06-01T00:00:00+00:00') ; assert tl[30].all_day == False
        assert tl[31].begin.datetime == dp('2016-06-19T00:00:00+00:00') ; assert tl[31].end.datetime == dp('2016-06-21T00:00:00+00:00') ; assert tl[31].all_day == True
        assert tl[32].begin.datetime == dp('2016-07-04T00:00:00+00:00') ; assert tl[32].end.datetime == dp('2016-07-06T00:00:00+00:00') ; assert tl[32].all_day == True
        assert tl[33].begin.datetime == dp('2016-07-14T00:00:00+00:00') ; assert tl[33].end.datetime == dp('2016-07-16T00:00:00+00:00') ; assert tl[33].all_day == True
        assert tl[34].begin.datetime == dp('2016-08-01T00:00:00+00:00') ; assert tl[34].end.datetime == dp('2016-08-03T00:00:00+00:00') ; assert tl[34].all_day == True
        assert tl[35].begin.datetime == dp('2016-08-15T00:00:00+00:00') ; assert tl[35].end.datetime == dp('2016-08-17T00:00:00+00:00') ; assert tl[35].all_day == True
        assert tl[36].begin.datetime == dp('2016-08-29T00:00:00+00:00') ; assert tl[36].end.datetime == dp('2016-08-31T00:00:00+00:00') ; assert tl[36].all_day == True
        assert tl[37].begin.datetime == dp('2016-09-05T00:00:00+00:00') ; assert tl[37].end.datetime == dp('2016-09-07T00:00:00+00:00') ; assert tl[37].all_day == True
        assert tl[38].begin.datetime == dp('2016-10-10T00:00:00+00:00') ; assert tl[38].end.datetime == dp('2016-10-12T00:00:00+00:00') ; assert tl[38].all_day == True
        assert tl[39].begin.datetime == dp('2016-10-31T00:00:00+00:00') ; assert tl[39].end.datetime == dp('2016-11-03T00:00:00+00:00') ; assert tl[39].all_day == False
        assert tl[40].begin.datetime == dp('2016-11-05T00:00:00+00:00') ; assert tl[40].end.datetime == dp('2016-11-07T00:00:00+00:00') ; assert tl[40].all_day == True
        assert tl[41].begin.datetime == dp('2016-11-11T00:00:00+00:00') ; assert tl[41].end.datetime == dp('2016-11-13T00:00:00+00:00') ; assert tl[41].all_day == False
        assert tl[42].begin.datetime == dp('2016-11-24T00:00:00+00:00') ; assert tl[42].end.datetime == dp('2016-11-26T00:00:00+00:00') ; assert tl[42].all_day == True
        assert tl[43].begin.datetime == dp('2016-12-25T00:00:00+00:00') ; assert tl[43].end.datetime == dp('2016-12-29T00:00:00+00:00') ; assert tl[43].all_day == False
        assert tl[44].begin.datetime == dp('2016-12-31T00:00:00+00:00') ; assert tl[44].end.datetime == dp('2017-01-02T00:00:00+00:00') ; assert tl[44].all_day == True

    def test_subscribe_calendar__file__single(self, datadir):
        self.cal.subscribe('file:///{}'.format(datadir['France-Holidays.ics']))
        self.check_first()

    def test_subscribe_calendar__file_merge_two(self, datadir):
        self.test_subscribe_calendar__file__single(datadir)
        self.cal.subscribe('file:///{}'.format(datadir['UK-Holidays.ics']))
        tl = list(self.cal._calendar_soup.timeline)
        self.check_second()

    def test_subscribe_calendar__file_merge_three(self, datadir):
        self.test_subscribe_calendar__file_merge_two(datadir)
        self.cal.subscribe('file:///{}'.format(datadir['US-Holidays.ics']))
        tl = list(self.cal._calendar_soup.timeline)
        self.check_third()

    def test_subscribe_calendar__http__single(self):
        self.cal.subscribe('http://www.calendarlabs.com/templates/ical/France-Holidays.ics')
        self.check_first()

    def test_subscribe_calendar__http_merge_two(self):
        self.test_subscribe_calendar__http__single()
        self.cal.subscribe('http://www.calendarlabs.com/templates/ical/UK-Holidays.ics')
        self.check_second()

    def test_subscribe_calendar__http_merge_three(self):
        self.test_subscribe_calendar__http_merge_two()
        self.cal.subscribe('webcal://www.calendarlabs.com/templates/ical/US-Holidays.ics')
        self.check_third()

    def test_add_event(self):
        uuids = []
        uuid = self.cal.add_event('Test #1', td(minutes=20))
        assert len(self.cal._pending.values()) == 1
        assert self.cal._pending[uuid].subject == 'Test #1'
        assert self.cal._pending[uuid].length == td(minutes=20)
        assert self.cal._pending[uuid].uuid == uuid
        uuids.append(uuid)
        uuid = self.cal.add_event('Test #2', td(hours=4))
        assert len(self.cal._pending.values()) == 2
        assert self.cal._pending[uuid].subject == 'Test #2'
        assert self.cal._pending[uuid].length == td(hours=4)
        assert self.cal._pending[uuid].uuid == uuid
        uuids.append(uuid)
        uuid = self.cal.add_event('Test #3', td(days=2))
        assert len(self.cal._pending.values()) == 3
        assert self.cal._pending[uuid].subject == 'Test #3'
        assert self.cal._pending[uuid].length == td(days=2)
        assert self.cal._pending[uuid].uuid == uuid
        uuids.append(uuid)
        uuid = self.cal.add_event('Test #4', td(minutes=90))
        assert len(self.cal._pending.values()) == 4
        assert self.cal._pending[uuid].subject == 'Test #4'
        assert self.cal._pending[uuid].length == td(minutes=90)
        assert self.cal._pending[uuid].uuid == uuid
        uuids.append(uuid)
        return uuids

    def test_confirm_event__inexists(self):
        with pytest.raises(Exception):
            self.cal.confirm_event('42', dt(2016, 6, 18, 20, 40))

    def test_confirm_event__first(self):
        uuids = self.test_add_event()
        self.cal.confirm_event(uuids[0], dt(2016, 6, 18, 20, 40))
        assert uuids[0] not in self.cal._pending
        assert len(self.cal._calendar_invites.events) == 1
        tl = list(self.cal._calendar_invites.timeline)
        assert tl[0].begin.datetime == dp('2016-06-18T20:40:00+00:00') ; assert tl[0].duration == td(minutes=20) ; assert tl[0].all_day == False
        return uuids

    def test_confirm_event__second(self):
        uuids = self.test_confirm_event__first()
        self.cal.confirm_event(uuids[1], dt(2016, 6, 18, 10, 40))
        assert uuids[1] not in self.cal._pending
        assert len(self.cal._calendar_invites.events) == 2
        tl = list(self.cal._calendar_invites.timeline)
        assert tl[1].begin.datetime == dp('2016-06-18T20:40:00+00:00') ; assert tl[1].duration == td(minutes=20) ; assert tl[1].all_day == False
        return uuids

    def test_confirm_event__third(self):
        uuids = self.test_confirm_event__second()
        self.cal.confirm_event(uuids[2], dt(2016, 6, 21, 12, 0))
        assert uuids[2] not in self.cal._pending
        assert len(self.cal._calendar_invites.events) == 3
        tl = list(self.cal._calendar_invites.timeline)
        assert tl[2].begin.datetime == dp('2016-06-21T12:00:00+00:00') ; assert tl[2].duration == td(days=2)     ; assert tl[2].all_day == False
        return uuids

    def test_confirm_event__fourth__no_avail(self):
        uuids = self.test_confirm_event__third()
        with pytest.raises(Exception):
            self.cal.confirm_event(uuids[3], dt(2016, 6, 21, 13, 0))
        return uuids

    def test_confirm_event__fourth(self):
        uuids = self.test_confirm_event__fourth__no_avail()
        self.cal.confirm_event(uuids[3], dt(2016, 6, 24, 12, 0))
        assert uuids[3] not in self.cal._pending
        assert len(self.cal._calendar_invites.events) == 4
        tl = list(self.cal._calendar_invites.timeline)
        assert tl[3].begin.datetime == dp('2016-06-24T12:00:00+00:00') ; assert tl[3].duration == td(minutes=90) ; assert tl[3].all_day == False

    def test_get_calendar(self, datadir):
        self.test_subscribe_calendar__file_merge_three(datadir)
        self.test_confirm_event__fourth()
        cal = self.cal.calendar
        tl = list(cal.timeline)
        assert tl[ 0].begin.datetime == dp('2015-01-01T00:00:00+00:00') ; assert tl[ 0].end.datetime == dp('2015-01-03T00:00:00+00:00') ; assert tl[ 0].all_day == False
        assert tl[ 1].begin.datetime == dp('2015-01-19T00:00:00+00:00') ; assert tl[ 1].end.datetime == dp('2015-01-21T00:00:00+00:00') ; assert tl[ 1].all_day == True
        assert tl[ 2].begin.datetime == dp('2015-02-14T00:00:00+00:00') ; assert tl[ 2].end.datetime == dp('2015-02-18T00:00:00+00:00') ; assert tl[ 2].all_day == False
        assert tl[ 3].begin.datetime == dp('2015-04-03T00:00:00+00:00') ; assert tl[ 3].end.datetime == dp('2015-04-08T00:00:00+00:00') ; assert tl[ 3].all_day == False
        assert tl[ 4].begin.datetime == dp('2015-05-01T00:00:00+00:00') ; assert tl[ 4].end.datetime == dp('2015-05-03T00:00:00+00:00') ; assert tl[ 4].all_day == True
        assert tl[ 5].begin.datetime == dp('2015-05-04T00:00:00+00:00') ; assert tl[ 5].end.datetime == dp('2015-05-06T00:00:00+00:00') ; assert tl[ 5].all_day == True
        assert tl[ 6].begin.datetime == dp('2015-05-08T00:00:00+00:00') ; assert tl[ 6].end.datetime == dp('2015-05-12T00:00:00+00:00') ; assert tl[ 6].all_day == False
        assert tl[ 7].begin.datetime == dp('2015-05-14T00:00:00+00:00') ; assert tl[ 7].end.datetime == dp('2015-05-16T00:00:00+00:00') ; assert tl[ 7].all_day == True
        assert tl[ 8].begin.datetime == dp('2015-05-24T00:00:00+00:00') ; assert tl[ 8].end.datetime == dp('2015-05-27T00:00:00+00:00') ; assert tl[ 8].all_day == False
        assert tl[ 9].begin.datetime == dp('2015-06-21T00:00:00+00:00') ; assert tl[ 9].end.datetime == dp('2015-06-23T00:00:00+00:00') ; assert tl[ 9].all_day == True
        assert tl[10].begin.datetime == dp('2015-07-04T00:00:00+00:00') ; assert tl[10].end.datetime == dp('2015-07-06T00:00:00+00:00') ; assert tl[10].all_day == True
        assert tl[11].begin.datetime == dp('2015-07-14T00:00:00+00:00') ; assert tl[11].end.datetime == dp('2015-07-16T00:00:00+00:00') ; assert tl[11].all_day == True
        assert tl[12].begin.datetime == dp('2015-08-03T00:00:00+00:00') ; assert tl[12].end.datetime == dp('2015-08-05T00:00:00+00:00') ; assert tl[12].all_day == True
        assert tl[13].begin.datetime == dp('2015-08-15T00:00:00+00:00') ; assert tl[13].end.datetime == dp('2015-08-17T00:00:00+00:00') ; assert tl[13].all_day == True
        assert tl[14].begin.datetime == dp('2015-08-31T00:00:00+00:00') ; assert tl[14].end.datetime == dp('2015-09-02T00:00:00+00:00') ; assert tl[14].all_day == True
        assert tl[15].begin.datetime == dp('2015-09-07T00:00:00+00:00') ; assert tl[15].end.datetime == dp('2015-09-09T00:00:00+00:00') ; assert tl[15].all_day == True
        assert tl[16].begin.datetime == dp('2015-10-12T00:00:00+00:00') ; assert tl[16].end.datetime == dp('2015-10-14T00:00:00+00:00') ; assert tl[16].all_day == True
        assert tl[17].begin.datetime == dp('2015-10-31T00:00:00+00:00') ; assert tl[17].end.datetime == dp('2015-11-03T00:00:00+00:00') ; assert tl[17].all_day == False
        assert tl[18].begin.datetime == dp('2015-11-05T00:00:00+00:00') ; assert tl[18].end.datetime == dp('2015-11-07T00:00:00+00:00') ; assert tl[18].all_day == True
        assert tl[19].begin.datetime == dp('2015-11-11T00:00:00+00:00') ; assert tl[19].end.datetime == dp('2015-11-13T00:00:00+00:00') ; assert tl[19].all_day == False
        assert tl[20].begin.datetime == dp('2015-11-26T00:00:00+00:00') ; assert tl[20].end.datetime == dp('2015-11-28T00:00:00+00:00') ; assert tl[20].all_day == True
        assert tl[21].begin.datetime == dp('2015-12-25T00:00:00+00:00') ; assert tl[21].end.datetime == dp('2015-12-28T00:00:00+00:00') ; assert tl[21].all_day == False
        assert tl[22].begin.datetime == dp('2015-12-31T00:00:00+00:00') ; assert tl[22].end.datetime == dp('2016-01-03T00:00:00+00:00') ; assert tl[22].all_day == False
        assert tl[23].begin.datetime == dp('2016-01-18T00:00:00+00:00') ; assert tl[23].end.datetime == dp('2016-01-20T00:00:00+00:00') ; assert tl[23].all_day == True
        assert tl[24].begin.datetime == dp('2016-02-14T00:00:00+00:00') ; assert tl[24].end.datetime == dp('2016-02-17T00:00:00+00:00') ; assert tl[24].all_day == False
        assert tl[25].begin.datetime == dp('2016-03-25T00:00:00+00:00') ; assert tl[25].end.datetime == dp('2016-03-30T00:00:00+00:00') ; assert tl[25].all_day == False
        assert tl[26].begin.datetime == dp('2016-05-01T00:00:00+00:00') ; assert tl[26].end.datetime == dp('2016-05-04T00:00:00+00:00') ; assert tl[26].all_day == False
        assert tl[27].begin.datetime == dp('2016-05-05T00:00:00+00:00') ; assert tl[27].end.datetime == dp('2016-05-07T00:00:00+00:00') ; assert tl[27].all_day == True
        assert tl[28].begin.datetime == dp('2016-05-08T00:00:00+00:00') ; assert tl[28].end.datetime == dp('2016-05-10T00:00:00+00:00') ; assert tl[28].all_day == False
        assert tl[29].begin.datetime == dp('2016-05-15T00:00:00+00:00') ; assert tl[29].end.datetime == dp('2016-05-18T00:00:00+00:00') ; assert tl[29].all_day == False
        assert tl[30].begin.datetime == dp('2016-05-30T00:00:00+00:00') ; assert tl[30].end.datetime == dp('2016-06-01T00:00:00+00:00') ; assert tl[30].all_day == False
        assert tl[31].begin.datetime == dp('2016-06-18T10:40:00+00:00') ; assert tl[31].end.datetime == dp('2016-06-18T14:40:00+00:00') ; assert tl[31].all_day == False
        assert tl[32].begin.datetime == dp('2016-06-18T20:40:00+00:00') ; assert tl[32].end.datetime == dp('2016-06-18T21:00:00+00:00') ; assert tl[32].all_day == False
        assert tl[33].begin.datetime == dp('2016-06-19T00:00:00+00:00') ; assert tl[33].end.datetime == dp('2016-06-21T00:00:00+00:00') ; assert tl[33].all_day == True
        assert tl[34].begin.datetime == dp('2016-06-21T12:00:00+00:00') ; assert tl[34].end.datetime == dp('2016-06-23T12:00:00+00:00') ; assert tl[34].all_day == False
        assert tl[35].begin.datetime == dp('2016-06-24T12:00:00+00:00') ; assert tl[35].end.datetime == dp('2016-06-24T13:30:00+00:00') ; assert tl[35].all_day == False
        assert tl[36].begin.datetime == dp('2016-07-04T00:00:00+00:00') ; assert tl[36].end.datetime == dp('2016-07-06T00:00:00+00:00') ; assert tl[36].all_day == True
        assert tl[37].begin.datetime == dp('2016-07-14T00:00:00+00:00') ; assert tl[37].end.datetime == dp('2016-07-16T00:00:00+00:00') ; assert tl[37].all_day == True
        assert tl[38].begin.datetime == dp('2016-08-01T00:00:00+00:00') ; assert tl[38].end.datetime == dp('2016-08-03T00:00:00+00:00') ; assert tl[38].all_day == True
        assert tl[39].begin.datetime == dp('2016-08-15T00:00:00+00:00') ; assert tl[39].end.datetime == dp('2016-08-17T00:00:00+00:00') ; assert tl[39].all_day == True
        assert tl[40].begin.datetime == dp('2016-08-29T00:00:00+00:00') ; assert tl[40].end.datetime == dp('2016-08-31T00:00:00+00:00') ; assert tl[40].all_day == True
        assert tl[41].begin.datetime == dp('2016-09-05T00:00:00+00:00') ; assert tl[41].end.datetime == dp('2016-09-07T00:00:00+00:00') ; assert tl[41].all_day == True
        assert tl[42].begin.datetime == dp('2016-10-10T00:00:00+00:00') ; assert tl[42].end.datetime == dp('2016-10-12T00:00:00+00:00') ; assert tl[42].all_day == True
        assert tl[43].begin.datetime == dp('2016-10-31T00:00:00+00:00') ; assert tl[43].end.datetime == dp('2016-11-03T00:00:00+00:00') ; assert tl[43].all_day == False
        assert tl[44].begin.datetime == dp('2016-11-05T00:00:00+00:00') ; assert tl[44].end.datetime == dp('2016-11-07T00:00:00+00:00') ; assert tl[44].all_day == True
        assert tl[45].begin.datetime == dp('2016-11-11T00:00:00+00:00') ; assert tl[45].end.datetime == dp('2016-11-13T00:00:00+00:00') ; assert tl[45].all_day == False
        assert tl[46].begin.datetime == dp('2016-11-24T00:00:00+00:00') ; assert tl[46].end.datetime == dp('2016-11-26T00:00:00+00:00') ; assert tl[46].all_day == True
        assert tl[47].begin.datetime == dp('2016-12-25T00:00:00+00:00') ; assert tl[47].end.datetime == dp('2016-12-29T00:00:00+00:00') ; assert tl[47].all_day == False
        assert tl[48].begin.datetime == dp('2016-12-31T00:00:00+00:00') ; assert tl[48].end.datetime == dp('2017-01-02T00:00:00+00:00') ; assert tl[48].all_day == True

    def test_get_busy_slots(self, datadir):
        from ics.utils import tzutc
        self.test_subscribe_calendar__file_merge_three(datadir)
        self.test_confirm_event__fourth()
        assert list(self.cal.get_busy_slots(dt(2016, 6, 16, tzinfo=tzutc), td(weeks=1))) == [
                (dt(2016, 6, 18, 10, 40, tzinfo=tzutc), dt(2016, 6, 18, 14, 40, tzinfo=tzutc)),
                (dt(2016, 6, 18, 20, 40, tzinfo=tzutc), dt(2016, 6, 18, 21, 0, tzinfo=tzutc)),
                (dt(2016, 6, 19, 0, 0, tzinfo=tzutc),   dt(2016, 6, 21, 0, 0, tzinfo=tzutc)),
                (dt(2016, 6, 21, 12, 0, tzinfo=tzutc),  dt(2016, 6, 23, 12, 0, tzinfo=tzutc))
                ]

    def test_refresh(self):
        # TODO make a test that changes the content of a calendar file before calling refresh
        pass



