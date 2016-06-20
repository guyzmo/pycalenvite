#!/usr/bin/env python

from functools import reduce

from base64 import urlsafe_b64encode
from uuid import uuid4

from requests import Session
from requests.adapters import HTTPAdapter
from urllib.parse import urlparse, urlunparse

from datetime import datetime, timedelta
from arrow.arrow import Arrow
dt_arrow = lambda dt: Arrow.fromdatetime(dt)

from ics import Calendar as CalendarBase, Event
from ics.timeline import Timeline

import logging
log = logging.getLogger('calenvite.calenvite')

from calenvite.exceptions import ResourceNotFound, ResourceConflict

DEFAULT_DOMAIN='localhost'


class WebcalAdapter(HTTPAdapter):
    def get_connection(self, url, proxies=None):
        url = 'http'+url[6:] if url.startswith('webcal') else url
        return super().get_connection(url, proxies)


class Calendar(CalendarBase):
    class EventUid:
        def __init__(self):
            self.uid = 0
        @property
        def next(self):
            try:
                return str(self.uid)
            finally:
                self.uid += 1

    def _reduce_overlaps(self, events, new_event):
        '''Internal method to check all events and merge them if necessary.
        Meant to be used within a reduced() function

        :param events: list of events
        :param new_event: event to insert or merge into another event
        :return: updated list of events
        '''
        uid = self.uid.next
        new_event.name = None
        log.debug('reduce: ? {} → {}'.format(repr(new_event), events))
        for event in events:
            if new_event.intersects(event):
                log.debug('reduce: ∩ {} ∩ {} → {}'.format(repr(new_event), repr(event), True))
                try:
                    events.remove(event)
                    events.add(event.join(new_event, uid=uid))
                    return events
                finally:
                    log.debug('reduce: ⇐1 {}'.format(events))
            log.debug('reduce: ∩ {} ∩ {} → {}'.format(repr(new_event), repr(event), False))
        new_event.uid = uid
        try:
            return events.union(set([new_event]))
        finally:
            log.debug('reduce: ⇐2 {}'.format(events.union(set([new_event]))))

    def merge(self, other: CalendarBase):
        '''merge an ICS calendar

        :other: calendar to merge events from
        :return: success in loading the ICS calendar
        '''
        events = set(self.events)

        for new_event in other.events:
            log.debug('merge: adding new event: {}'.format(repr(new_event)))
            for event in events:
                log.debug('merge: checking event: {}'.format(repr(event)))
                if event.intersects(new_event):
                    events.remove(event)
                    events.add(event.join(new_event))
                    log.debug('merge: {} ∪ {}'.format(event.uid, new_event.uid))
                    break
                else:
                    log.debug('merge: !∩ {} !∩ {}'.format(repr(event), repr(new_event)))
            else:
                events.add(new_event.clone())

        self.uid = Calendar.EventUid()
        self.events = reduce(self._reduce_overlaps, events, set())

    def has_slot(self, other: Event):
        '''Tells if there's a free slot for event

        :param other: the event to test against
        :return: True if there's a free slot
        '''
        for event in self.events:
            if event.intersects(other):
                return False
        return True

Event.__json__ = lambda ev: dict(name=ev.name, uid=ev.uid, begin=ev.begin, end=ev.end)

class PendingEvent:
    '''Represents a pending event. 

    It is defined by a subject and length, and gets an unique identifier.
    '''
    def __init__(self, subject: str, length: timedelta, uuid: str):
        self.subject = subject
        self.length = length
        self.uuid = uuid

    def as_event(self, time: datetime):
        return Event(name=self.subject, 
                uid='{}@{}'.format(self.uuid, DEFAULT_DOMAIN),
                duration=self.length,
                begin=time)

    def __json__(self):
        return dict(subject=self.subject, length=self.length, uuid=self.uuid)

class Calenvite:
    def __init__(self):
        self._subscriptions = []
        self._calendar_soup = Calendar()
        self._calendar_invites = Calendar()
        self._pending = {}
        self._session = Session()
        self._session.mount('webcal', WebcalAdapter())

    @property
    def subscriptions(self):
        return self._subscriptions

    @property
    def calendar(self):
        '''Gets the calendar with confirmed invites

        :return: ICS with those invites'''
        calendar = Calendar()
        calendar.merge(self._calendar_soup)
        calendar.merge(self._calendar_invites)
        return calendar

    @property
    def invites(self):
        return self._pending.values()

    @property
    def meetings(self):
        return self._calendar_invites

    def subscribe(self, uri: str):
        '''Subscribe to an external calendar into internal one.

        :return: success in loading the ICS calendar
        '''
        self._subscriptions.append(uri)
        uri = urlparse(uri)
        if uri.scheme == 'file':
            calendar = Calendar(open(uri.path, 'r'))
        elif uri.scheme == 'http' or uri.scheme == 'https' or uri.scheme == 'webcal':
            calendar = Calendar(self._session.get(urlunparse(uri)).text)

        self._calendar_soup.merge(calendar)

    def refresh(self):
        self._calendar_soup = Calendar()
        for uri in self._subscriptions:
            self.subscribe(uri)

    def _generate_uuid(self):
        '''Generates unique UUID (internal method)

        and makes /sure/ there's no collision in pending events list.
        '''
        uuid = None
        while not uuid:
            uuid = urlsafe_b64encode(uuid4().bytes).replace(b'=', b'')
            if uuid in self._pending: # pragma: no cover
                uuid = None
        return uuid.decode('utf-8')

    def show_invite(self, uuid):
        '''Returns a stored invitation (or None)
        '''
        return self._pending.get(uuid, None)

    def create_invite(self, subject: str, length: timedelta):
        '''Creates a new event to be confirmed

        :return: unique hash'''
        uuid = self._generate_uuid()
        self._pending[uuid] = PendingEvent(subject, length, uuid)
        return self._pending[uuid]

    def confirm_invite(self, uuid: str, time: datetime):
        '''Confirms an event with given uuid

        :return: Confirmed event'''
        if uuid not in self._pending:
            raise ResourceNotFound('No event is referenced by UUID')

        event = self._pending[uuid].as_event(time)

        if not self._calendar_soup.has_slot(event) or not self._calendar_invites.has_slot(event):
            raise ResourceConflict('No availability for event at chosen time.')

        self._calendar_invites.events.add(event)
        del(self._pending[uuid])

        return event

    def get_busy_slots(self, date: datetime, delta: timedelta):
        '''Gets list of slots marked as busy

        :param date: a day for which to get events

        :return: list of time ranges (tuples with start/end times)'''
        for event in self.calendar.timeline.start_after(dt_arrow(date)):
            if event.begin < dt_arrow(date+delta):
                yield (event.begin.datetime, event.end.datetime)





