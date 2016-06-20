#!/usr/bin/env python

from isodate import duration_isoformat as iso_td, datetime_isoformat as iso_dt
from datetime import timedelta as td, datetime as dt

from flask import url_for

import pytest

'''Classes to prepare the tests'''


@pytest.mark.usefixtures('client_class', 'datadir_class')
class FixturesMixin: pass


class CalenviteClientListerMixin:
    def list_invitations(self, **kwarg):
        res = self.client.get(url_for('invitationlist', **kwarg))
        assert res.status_code == 200
        return res.json

    def list_calendar_slots(self, **kwarg):
        print('xxx', kwarg)
        res = self.client.get(url_for('calendarslots', **kwarg))
        assert res.status_code == 200
        return res.json

    def list_calendar_meetings(self, **kwarg):
        res = self.client.get(url_for('calendarmeetings', **kwarg))
        assert res.status_code == 200
        return res.json

    def list_calendar_soup(self, **kwarg):
        res = self.client.get(url_for('calendarsoup', **kwarg))
        assert res.status_code == 200
        return res.json

    def list_calendar_subscriptions(self, **kwarg):
        res = self.client.get(url_for('calendarsubscriptionlist', **kwarg))
        assert res.status_code == 200
        return res.json


class CalenviteClientGetterMixin:
    def get_invitation(self, uuid, status=200):
        res = self.client.get(url_for('invitation', uuid=uuid))
        assert res.status_code == status
        return res.json

    def get_calendar_subscription(self, idx, status=200):
        res = self.client.get(url_for('calendarsubscription', index=idx))
        assert res.status_code == status
        return res.json


class CalenviteClientMutatorMixin:
    def create_invitation(self, subject, length, status=201):
        res = self.client.post(url_for('invitation', subject=subject, length=length))
        assert res.status_code == status
        return res.json

    def accept_invitation(self, uuid, date, status=200):
        res = self.client.post(url_for('invitation',
            uuid=uuid,
            date=date))
        assert res.status_code == status
        return res.json

    def subscribe_calendar(self, url, status=204):
        res = self.client.post(url_for('calendarsubscription', url=url))
        assert res.status_code == status
        assert res.data == b''

    def delete_calendar(self, url, status=200):
        res = self.client.delete(url_for('calendarsubscription', url=url))
        assert res.status_code == status
        return res.json


class CalenviteSubscription(CalenviteClientMutatorMixin, CalenviteClientListerMixin):
    def do_one_http_subscription(self):
        '''Adding one calendar subscription'''
        self.subscribe_calendar('http://www.calendarlabs.com/templates/ical/US-Holidays.ics')
        res = self.list_calendar_subscriptions()
        assert res == ['http://www.calendarlabs.com/templates/ical/US-Holidays.ics']

    def do_two_http_subscriptions(self):
        '''Adding one calendar subscription'''
        self.do_one_http_subscription()
        self.subscribe_calendar('http://www.calendarlabs.com/templates/ical/UK-Holidays.ics')
        res = self.list_calendar_subscriptions()
        assert res == [
                'http://www.calendarlabs.com/templates/ical/US-Holidays.ics',
                'http://www.calendarlabs.com/templates/ical/UK-Holidays.ics',
                ]

    def do_three_http_subscriptions(self):
        '''Adding one calendar subscription'''
        self.do_two_http_subscriptions()
        self.subscribe_calendar('http://www.calendarlabs.com/templates/ical/France-Holidays.ics')
        res = self.list_calendar_subscriptions()
        assert res == [
                'http://www.calendarlabs.com/templates/ical/US-Holidays.ics',
                'http://www.calendarlabs.com/templates/ical/UK-Holidays.ics',
                'http://www.calendarlabs.com/templates/ical/France-Holidays.ics',
                ]

    def do_one_file_subscription(self):
        '''Adding one calendar subscription'''
        self.subscribe_calendar('file:///{}'.format(self.datadir['US-Holidays.ics']))
        res = self.list_calendar_subscriptions()
        assert res == ['file:///{}'.format(self.datadir['US-Holidays.ics'])]

    def do_two_file_subscriptions(self):
        '''Adding one calendar subscription'''
        self.do_one_file_subscription()
        self.subscribe_calendar('file:///{}'.format(self.datadir['UK-Holidays.ics']))
        res = self.list_calendar_subscriptions()
        assert res == [
                'file:///{}'.format(self.datadir['US-Holidays.ics']),
                'file:///{}'.format(self.datadir['UK-Holidays.ics']),
                ]

    def do_three_file_subscriptions(self):
        '''Adding one calendar subscription'''
        self.do_two_file_subscriptions()
        self.subscribe_calendar('file:///{}'.format(self.datadir['France-Holidays.ics']))
        res = self.list_calendar_subscriptions()
        assert res == [
                'file:///{}'.format(self.datadir['US-Holidays.ics']),
                'file:///{}'.format(self.datadir['UK-Holidays.ics']),
                'file:///{}'.format(self.datadir['France-Holidays.ics']),
                ]


class CalenviteInvitations(CalenviteClientGetterMixin, CalenviteClientMutatorMixin, CalenviteClientListerMixin):

    def do_create_invitations(self, deltas=[]):
        l_orig = self.list_invitations()
        results = []
        for i in range(0, len(deltas)):
            res = self.create_invitation('Test #{:02d}'.format(i+1),
                    length=iso_td(deltas[i]))
            l = self.list_invitations()
            assert len(l) == len(l_orig)+1
            l_orig = l
            results += [res]
        return results

    def do_create_one_invitation(self):
        return self.do_create_invitations([td(minutes=20)])

    def do_create_two_invitations(self):
        return self.do_create_invitations([
            td(minutes=20),
            td(hours=2)])

    def do_create_three_invitations(self):
        return self.do_create_invitations([
            td(minutes=20),
            td(hours=2),
            td(days=2)])

    def do_accept_invitation(self, uuid, date, status=200):
        nb_inv = len(self.list_invitations())
        res = self.accept_invitation(uuid, date, status)
        if status == 200:
            assert len(self.list_invitations()) == nb_inv-1
        elif status > 400:
            assert len(self.list_invitations()) == nb_inv
        return res

####################################################################################

'''The actual test suite'''

class TestCalendarSubscription(FixturesMixin, CalenviteSubscription):
    def test_empty(self):
        res = self.list_calendar_subscriptions()
        assert res == []

    def test_http_calendars(self):
        self.do_three_http_subscriptions()

    def test_file_calendars(self):
        self.do_three_file_subscriptions()


class TestCalendarInvitations__unpopulated(FixturesMixin, CalenviteInvitations):
    def test_get_invitation__without_uuid(self):
        ''' GET /invitation
        '''
        res = self.client.get(url_for('invitation'))
        assert res.status_code == 500
        assert res.json == {'message': 'Internal Server Error'}

    def test_get_invitation_uuid__doesnotexists(self):
        ''' GET /invitation/doesnotexists
        '''
        res = self.get_invitation(uuid='doesnotexists', status=404)
        assert res == {'message': 'The requested resource does not exists.', 'status': 404}

    def test_accept_invitation__doesnotexists(self):
        res = self.accept_invitation(uuid='doesnotexists',
                date=iso_dt(dt(2016, 6, 19, 0, 0, 0)),
                status=404)
        assert res == {'message': 'The requested resource does not exists.', 'status': 404}

    def test_list_invitations(self):
        res = self.list_invitations()
        assert res == []


class TestInvitationsAPI__no_calendar(FixturesMixin, CalenviteInvitations):
    def test_create_1_invitation(self):
        self.do_create_one_invitation()

    def test_create_2_invitations(self):
        self.do_create_two_invitations()

    def test_create_3_invitations(self):
        self.do_create_three_invitations()

    def test_accept_1_invitation(self):
        prev = self.do_create_one_invitation()
        res = self.do_accept_invitation(prev[0]['uuid'], iso_dt(dt(2016, 6, 20, 12, 0)))
        assert res['name']  == 'Test #01'
        assert res['begin'] == '2016-06-20T12:00:00Z'
        assert res['end']   == '2016-06-20T12:20:00Z'
        assert res['uid']  == '{}@localhost'.format(prev[0]['uuid'])

    def test_accept_2_invitations(self):
        prev = self.do_create_two_invitations()
        res = self.do_accept_invitation(prev[0]['uuid'], iso_dt(dt(2016, 6, 20, 12, 0)))
        assert res['name']  == 'Test #01'
        assert res['begin'] == '2016-06-20T12:00:00Z'
        assert res['end']   == '2016-06-20T12:20:00Z'
        assert res['uid']  == '{}@localhost'.format(prev[0]['uuid'])
        res = self.do_accept_invitation(prev[1]['uuid'], iso_dt(dt(2016, 6, 21, 12, 0)))
        assert res['name']  == 'Test #02'
        assert res['begin'] == '2016-06-21T12:00:00Z'
        assert res['end']   == '2016-06-21T14:00:00Z'
        assert res['uid']  == '{}@localhost'.format(prev[1]['uuid'])

    def test_accept_3_invitations(self):
        prev = self.do_create_three_invitations()
        res = self.do_accept_invitation(prev[0]['uuid'], iso_dt(dt(2016, 6, 20, 12, 0)))
        assert res['name']  == 'Test #01'
        assert res['begin'] == '2016-06-20T12:00:00Z'
        assert res['end']   == '2016-06-20T12:20:00Z'
        assert res['uid']  == '{}@localhost'.format(prev[0]['uuid'])
        res = self.do_accept_invitation(prev[1]['uuid'], iso_dt(dt(2016, 6, 21, 12, 0)))
        assert res['name']  == 'Test #02'
        assert res['begin'] == '2016-06-21T12:00:00Z'
        assert res['end']   == '2016-06-21T14:00:00Z'
        assert res['uid']  == '{}@localhost'.format(prev[1]['uuid'])
        res = self.do_accept_invitation(prev[2]['uuid'], iso_dt(dt(2016, 6, 22, 12, 0)))
        assert res['name']  == 'Test #03'
        assert res['begin'] == '2016-06-22T12:00:00Z'
        assert res['end']   == '2016-06-24T12:00:00Z'
        assert res['uid']  == '{}@localhost'.format(prev[2]['uuid'])

    def test_accept_3_invitations__conflict_1_2(self):
        prev = self.do_create_three_invitations()
        res = self.do_accept_invitation(prev[0]['uuid'], iso_dt(dt(2016, 6, 20, 12, 10)))
        assert res['name']  == 'Test #01'
        assert res['begin'] == '2016-06-20T12:10:00Z'
        assert res['end']   == '2016-06-20T12:30:00Z'
        assert res['uid']  == '{}@localhost'.format(prev[0]['uuid'])
        res = self.do_accept_invitation(prev[1]['uuid'], iso_dt(dt(2016, 6, 20, 12, 0)), 409)
        assert res == {'message': 'The query cannot be fulfilled because of a conflict.', 'status': 409}
        res = self.do_accept_invitation(prev[2]['uuid'], iso_dt(dt(2016, 6, 22, 12, 0)))
        assert res['name']  == 'Test #03'
        assert res['begin'] == '2016-06-22T12:00:00Z'
        assert res['end']   == '2016-06-24T12:00:00Z'
        assert res['uid']  == '{}@localhost'.format(prev[2]['uuid'])

    def test_accept_3_invitations__conflict_1_3(self):
        prev = self.do_create_three_invitations()
        res = self.do_accept_invitation(prev[0]['uuid'], iso_dt(dt(2016, 6, 20, 12, 0)))
        assert res['name']  == 'Test #01'
        assert res['begin'] == '2016-06-20T12:00:00Z'
        assert res['end']   == '2016-06-20T12:20:00Z'
        assert res['uid']  == '{}@localhost'.format(prev[0]['uuid'])
        res = self.do_accept_invitation(prev[1]['uuid'], iso_dt(dt(2016, 6, 19, 12, 0)))
        assert res['name']  == 'Test #02'
        assert res['begin'] == '2016-06-19T12:00:00Z'
        assert res['end']   == '2016-06-19T14:00:00Z'
        assert res['uid']  == '{}@localhost'.format(prev[1]['uuid'])
        res = self.do_accept_invitation(prev[2]['uuid'], iso_dt(dt(2016, 6, 20, 0, 0)), 409)
        assert res == {'message': 'The query cannot be fulfilled because of a conflict.', 'status': 409}

    def test_accept_3_invitations__conflict_2_3(self):
        prev = self.do_create_three_invitations()
        res = self.do_accept_invitation(prev[0]['uuid'], iso_dt(dt(2016, 6, 19, 12, 0)))
        assert res['name']  == 'Test #01'
        assert res['begin'] == '2016-06-19T12:00:00Z'
        assert res['end']   == '2016-06-19T12:20:00Z'
        assert res['uid']  == '{}@localhost'.format(prev[0]['uuid'])
        res = self.do_accept_invitation(prev[1]['uuid'], iso_dt(dt(2016, 6, 20, 12, 0)))
        assert res['name']  == 'Test #02'
        assert res['begin'] == '2016-06-20T12:00:00Z'
        assert res['end']   == '2016-06-20T14:00:00Z'
        assert res['uid']  == '{}@localhost'.format(prev[1]['uuid'])
        res = self.do_accept_invitation(prev[2]['uuid'], iso_dt(dt(2016, 6, 20, 0, 0)), 409)
        assert res == {'message': 'The query cannot be fulfilled because of a conflict.', 'status': 409}

    def test_accept_3_invitations__conflict_2_3_1(self):
        prev = self.do_create_three_invitations()
        res = self.do_accept_invitation(prev[0]['uuid'], iso_dt(dt(2016, 6, 20, 12, 10)))
        assert res['name']  == 'Test #01'
        assert res['begin'] == '2016-06-20T12:10:00Z'
        assert res['end']   == '2016-06-20T12:30:00Z'
        assert res['uid']  == '{}@localhost'.format(prev[0]['uuid'])
        res = self.do_accept_invitation(prev[1]['uuid'], iso_dt(dt(2016, 6, 20, 12, 0)), 409)
        assert res == {'message': 'The query cannot be fulfilled because of a conflict.', 'status': 409}
        res = self.do_accept_invitation(prev[2]['uuid'], iso_dt(dt(2016, 6, 20, 0, 0)), 409)
        assert res == {'message': 'The query cannot be fulfilled because of a conflict.', 'status': 409}

    def test_list_invitations__paginate(self):
        prev = self.do_create_invitations([
            td(minutes=10), td(hours=1), td(days=1), 
            td(minutes=20), td(hours=2), td(days=2), 
            td(minutes=30), td(hours=3), td(days=3), 
            td(minutes=40), td(hours=4), td(days=4), 
            td(minutes=50), td(hours=5), td(days=5), 
            ])
        # total no pagination
        res = self.list_invitations(ordering='subject')
        sort_key = lambda x: x['subject']
        assert res == [
                {'length': 'PT10M', 'subject': 'Test #01', 'uuid':  prev[0]['uuid']},
                {'length': 'PT1H',  'subject': 'Test #02', 'uuid':  prev[1]['uuid']},
                {'length': 'P1D',   'subject': 'Test #03', 'uuid':  prev[2]['uuid']},
                {'length': 'PT20M', 'subject': 'Test #04', 'uuid':  prev[3]['uuid']},
                {'length': 'PT2H',  'subject': 'Test #05', 'uuid':  prev[4]['uuid']},
                {'length': 'P2D',   'subject': 'Test #06', 'uuid':  prev[5]['uuid']},
                {'length': 'PT30M', 'subject': 'Test #07', 'uuid':  prev[6]['uuid']},
                {'length': 'PT3H',  'subject': 'Test #08', 'uuid':  prev[7]['uuid']},
                {'length': 'P3D',   'subject': 'Test #09', 'uuid':  prev[8]['uuid']},
                {'length': 'PT40M', 'subject': 'Test #10', 'uuid': prev[9]['uuid']},
                {'length': 'PT4H',  'subject': 'Test #11', 'uuid': prev[10]['uuid']},
                {'length': 'P4D',   'subject': 'Test #12', 'uuid': prev[11]['uuid']},
                {'length': 'PT50M', 'subject': 'Test #13', 'uuid': prev[12]['uuid']},
                {'length': 'PT5H',  'subject': 'Test #14', 'uuid': prev[13]['uuid']},
                {'length': 'P5D',   'subject': 'Test #15', 'uuid': prev[14]['uuid']},
                ]
        # page 1, 5 per page
        res = self.list_invitations(page=0, per_page=5, ordering='subject')
        sort_key = lambda x: x['subject']
        assert res == [
                {'length': 'PT10M', 'subject': 'Test #01', 'uuid':  prev[0]['uuid']},
                {'length': 'PT1H',  'subject': 'Test #02', 'uuid':  prev[1]['uuid']},
                {'length': 'P1D',   'subject': 'Test #03', 'uuid':  prev[2]['uuid']},
                {'length': 'PT20M', 'subject': 'Test #04', 'uuid':  prev[3]['uuid']},
                {'length': 'PT2H',  'subject': 'Test #05', 'uuid':  prev[4]['uuid']},
                ]
        # page 2, 5 per page
        res = self.list_invitations(page=1, per_page=5, ordering='subject')
        sort_key = lambda x: x['subject']
        assert res == [
                {'length': 'P2D',   'subject': 'Test #06', 'uuid':  prev[5]['uuid']},
                {'length': 'PT30M', 'subject': 'Test #07', 'uuid':  prev[6]['uuid']},
                {'length': 'PT3H',  'subject': 'Test #08', 'uuid':  prev[7]['uuid']},
                {'length': 'P3D',   'subject': 'Test #09', 'uuid':  prev[8]['uuid']},
                {'length': 'PT40M', 'subject': 'Test #10', 'uuid':  prev[9]['uuid']},
                ]
        # page 3, 5 per page
        res = self.list_invitations(page=2, per_page=5, ordering='subject')
        sort_key = lambda x: x['subject']
        assert res == [
                {'length': 'PT4H',  'subject': 'Test #11', 'uuid': prev[10]['uuid']},
                {'length': 'P4D',   'subject': 'Test #12', 'uuid': prev[11]['uuid']},
                {'length': 'PT50M', 'subject': 'Test #13', 'uuid': prev[12]['uuid']},
                {'length': 'PT5H',  'subject': 'Test #14', 'uuid': prev[13]['uuid']},
                {'length': 'P5D',  'subject': 'Test #15', 'uuid': prev[14]['uuid']},
                ]
        # reversed ordering
        # page 3, 5 per page
        res = self.list_invitations(page=0, per_page=5, ordering='-subject')
        sort_key = lambda x: x['subject']
        assert res == [
                {'length': 'P5D',  'subject': 'Test #15', 'uuid': prev[14]['uuid']},
                {'length': 'PT5H',  'subject': 'Test #14', 'uuid': prev[13]['uuid']},
                {'length': 'PT50M', 'subject': 'Test #13', 'uuid': prev[12]['uuid']},
                {'length': 'P4D',   'subject': 'Test #12', 'uuid': prev[11]['uuid']},
                {'length': 'PT4H',  'subject': 'Test #11', 'uuid': prev[10]['uuid']},
                ]


class TestInvitationsAPI__with_calendars(FixturesMixin, CalenviteSubscription, CalenviteInvitations):
    def test_create_1_invitation(self):
        self.do_three_file_subscriptions()
        self.do_create_one_invitation()

    def test_create_2_invitations(self):
        self.do_three_file_subscriptions()
        self.do_create_two_invitations()

    def test_create_3_invitations(self):
        self.do_three_file_subscriptions()
        self.do_create_three_invitations()

    def test_accept_1_invitation(self):
        self.do_three_file_subscriptions()
        prev = self.do_create_one_invitation()
        res = self.do_accept_invitation(prev[0]['uuid'], iso_dt(dt(2016, 6, 12, 12, 0)))
        assert res['name']  == 'Test #01'
        assert res['begin'] == '2016-06-12T12:00:00Z'
        assert res['end']   == '2016-06-12T12:20:00Z'
        assert res['uid']  == '{}@localhost'.format(prev[0]['uuid'])


    def test_accept_2_invitations(self):
        self.do_three_file_subscriptions()
        prev = self.do_create_two_invitations()
        res = self.do_accept_invitation(prev[0]['uuid'], iso_dt(dt(2016, 6, 12, 12, 0)))
        assert res['name']  == 'Test #01'
        assert res['begin'] == '2016-06-12T12:00:00Z'
        assert res['end']   == '2016-06-12T12:20:00Z'
        assert res['uid']  == '{}@localhost'.format(prev[0]['uuid'])
        res = self.do_accept_invitation(prev[1]['uuid'], iso_dt(dt(2016, 6, 21, 12, 0)))
        assert res['name']  == 'Test #02'
        assert res['begin'] == '2016-06-21T12:00:00Z'
        assert res['end']   == '2016-06-21T14:00:00Z'
        assert res['uid']  == '{}@localhost'.format(prev[1]['uuid'])

    def test_accept_3_invitations(self):
        self.do_three_file_subscriptions()
        prev = self.do_create_three_invitations()
        res = self.do_accept_invitation(prev[0]['uuid'], iso_dt(dt(2016, 6, 12, 12, 0)))
        assert res['name']  == 'Test #01'
        assert res['begin'] == '2016-06-12T12:00:00Z'
        assert res['end']   == '2016-06-12T12:20:00Z'
        assert res['uid']  == '{}@localhost'.format(prev[0]['uuid'])
        res = self.do_accept_invitation(prev[1]['uuid'], iso_dt(dt(2016, 6, 21, 12, 0)))
        assert res['name']  == 'Test #02'
        assert res['begin'] == '2016-06-21T12:00:00Z'
        assert res['end']   == '2016-06-21T14:00:00Z'
        assert res['uid']  == '{}@localhost'.format(prev[1]['uuid'])
        res = self.do_accept_invitation(prev[2]['uuid'], iso_dt(dt(2016, 6, 22, 12, 0)))
        assert res['name']  == 'Test #03'
        assert res['begin'] == '2016-06-22T12:00:00Z'
        assert res['end']   == '2016-06-24T12:00:00Z'
        assert res['uid']  == '{}@localhost'.format(prev[2]['uuid'])

    def test_accept_3_invitations__conflict_1_2(self):
        self.do_three_file_subscriptions()
        prev = self.do_create_three_invitations()
        res = self.do_accept_invitation(prev[0]['uuid'], iso_dt(dt(2016, 6, 12, 12, 10)))
        assert res['name']  == 'Test #01'
        assert res['begin'] == '2016-06-12T12:10:00Z'
        assert res['end']   == '2016-06-12T12:30:00Z'
        assert res['uid']  == '{}@localhost'.format(prev[0]['uuid'])
        res = self.do_accept_invitation(prev[1]['uuid'], iso_dt(dt(2016, 6, 20, 12, 0)), 409)
        assert res == {'message': 'The query cannot be fulfilled because of a conflict.', 'status': 409}
        res = self.do_accept_invitation(prev[2]['uuid'], iso_dt(dt(2016, 6, 22, 12, 0)))
        assert res['name']  == 'Test #03'
        assert res['begin'] == '2016-06-22T12:00:00Z'
        assert res['end']   == '2016-06-24T12:00:00Z'
        assert res['uid']  == '{}@localhost'.format(prev[2]['uuid'])

    def test_accept_3_invitations__conflict_1_3(self):
        self.do_three_file_subscriptions()
        prev = self.do_create_three_invitations()
        res = self.do_accept_invitation(prev[0]['uuid'], iso_dt(dt(2016, 6, 12, 12, 0)))
        assert res['name']  == 'Test #01'
        assert res['begin'] == '2016-06-12T12:00:00Z'
        assert res['end']   == '2016-06-12T12:20:00Z'
        assert res['uid']  == '{}@localhost'.format(prev[0]['uuid'])
        res = self.do_accept_invitation(prev[1]['uuid'], iso_dt(dt(2016, 6, 17, 12, 0)))
        assert res['name']  == 'Test #02'
        assert res['begin'] == '2016-06-17T12:00:00Z'
        assert res['end']   == '2016-06-17T14:00:00Z'
        assert res['uid']  == '{}@localhost'.format(prev[1]['uuid'])
        res = self.do_accept_invitation(prev[2]['uuid'], iso_dt(dt(2016, 6, 20, 0, 0)), 409)
        assert res == {'message': 'The query cannot be fulfilled because of a conflict.', 'status': 409}

    def test_accept_3_invitations__conflict_2_3(self):
        self.do_three_file_subscriptions()
        prev = self.do_create_three_invitations()
        res = self.do_accept_invitation(prev[0]['uuid'], iso_dt(dt(2016, 6, 12, 12, 0)))
        assert res['name']  == 'Test #01'
        assert res['begin'] == '2016-06-12T12:00:00Z'
        assert res['end']   == '2016-06-12T12:20:00Z'
        assert res['uid']  == '{}@localhost'.format(prev[0]['uuid'])
        res = self.do_accept_invitation(prev[1]['uuid'], iso_dt(dt(2016, 6, 15, 12, 0)))
        assert res['name']  == 'Test #02'
        assert res['begin'] == '2016-06-15T12:00:00Z'
        assert res['end']   == '2016-06-15T14:00:00Z'
        assert res['uid']  == '{}@localhost'.format(prev[1]['uuid'])
        res = self.do_accept_invitation(prev[2]['uuid'], iso_dt(dt(2016, 6, 20, 0, 0)), 409)
        assert res == {'message': 'The query cannot be fulfilled because of a conflict.', 'status': 409}

    def test_accept_3_invitations__conflict_2_3_1(self):
        self.do_three_file_subscriptions()
        prev = self.do_create_three_invitations()
        res = self.do_accept_invitation(prev[0]['uuid'], iso_dt(dt(2016, 6, 12, 12, 10)))
        assert res['name']  == 'Test #01'
        assert res['begin'] == '2016-06-12T12:10:00Z'
        assert res['end']   == '2016-06-12T12:30:00Z'
        assert res['uid']  == '{}@localhost'.format(prev[0]['uuid'])
        res = self.do_accept_invitation(prev[1]['uuid'], iso_dt(dt(2016, 6, 12, 12, 0)), 409)
        assert res == {'message': 'The query cannot be fulfilled because of a conflict.', 'status': 409}
        res = self.do_accept_invitation(prev[2]['uuid'], iso_dt(dt(2016, 6, 11, 0, 0)), 409)
        assert res == {'message': 'The query cannot be fulfilled because of a conflict.', 'status': 409}

    def test_accept_3_invitations__conflicts(self):
        self.do_three_file_subscriptions()
        prev = self.do_create_three_invitations()
        res = self.do_accept_invitation(prev[0]['uuid'], iso_dt(dt(2016, 7, 4, 12, 0)), 409)
        assert res == {'message': 'The query cannot be fulfilled because of a conflict.', 'status': 409}
        res = self.do_accept_invitation(prev[1]['uuid'], iso_dt(dt(2016, 7, 14, 12, 0)), 409)
        assert res == {'message': 'The query cannot be fulfilled because of a conflict.', 'status': 409}
        res = self.do_accept_invitation(prev[2]['uuid'], iso_dt(dt(2016, 12, 26, 0, 0)), 409)
        assert res == {'message': 'The query cannot be fulfilled because of a conflict.', 'status': 409}

class TestCalendarsAPI__with_calendars(FixturesMixin, CalenviteSubscription, CalenviteInvitations):
    def prepare_accept_3_invitations_3_subscriptions(self):
        self.do_three_file_subscriptions()
        prev = self.do_create_three_invitations()
        res = self.do_accept_invitation(prev[0]['uuid'], iso_dt(dt(2016, 6, 12, 12, 0)))
        assert res['name']  == 'Test #01'
        assert res['begin'] == '2016-06-12T12:00:00Z'
        assert res['end']   == '2016-06-12T12:20:00Z'
        assert res['uid']  == '{}@localhost'.format(prev[0]['uuid'])
        res = self.do_accept_invitation(prev[1]['uuid'], iso_dt(dt(2016, 6, 13, 12, 0)))
        assert res['name']  == 'Test #02'
        assert res['begin'] == '2016-06-13T12:00:00Z'
        assert res['end']   == '2016-06-13T14:00:00Z'
        assert res['uid']  == '{}@localhost'.format(prev[1]['uuid'])
        res = self.do_accept_invitation(prev[2]['uuid'], iso_dt(dt(2016, 6, 14, 12, 0)))
        assert res['name']  == 'Test #03'
        assert res['begin'] == '2016-06-14T12:00:00Z'
        assert res['end']   == '2016-06-16T12:00:00Z'
        assert res['uid']  == '{}@localhost'.format(prev[2]['uuid'])
        return prev

    def _parse_ics_string(self, ics, sort_key='SUMMARY'):
        """Parse an ICS and returns elements in a predictable way"""
        def _format_events(events):
            res = []
            for ev in events:
                ev_dict = {}
                for line in sorted(ev.split('\r\n')):
                    if 'DTSTART;VALUE=DATE':
                        line.replace('DTSTART;VALUE=DATE', 'DTSTART')
                    # filter out all mutables and meaningless
                    if 'LAST-MODIFIED:' in line: continue
                    elif 'DTSTAMP:' in line: continue
                    elif 'CREATED:' in line: continue
                    elif 'END:VEVENT' in line: continue
                    elif 'END:VCALENDAR' in line: continue
                    elif line == '': continue
                    key, *val = line.split(':')
                    ev_dict[key] = ':'.join(val)
                res.append(ev_dict)
            # sort over the summary text
            return sorted(res, key=lambda x: x[sort_key])

        # extracting all events
        header, *events = ics.split('BEGIN:VEVENT')

        return header.split('\r\n'), _format_events(events)

    def test_get_calendar_meetings_ics(self):
        prev = self.prepare_accept_3_invitations_3_subscriptions()
        ics = self.list_calendar_meetings()
        header, events = self._parse_ics_string(ics)

        assert [
            'BEGIN:VCALENDAR',
            'PRODID:ics.py - http://git.io/lLljaA',
            'VERSION:2.0',
            ''] == header

        assert {'DTSTART': '20160612T120000Z',
                'DURATION': 'PT20M',
                'SUMMARY': 'Test #01',
                'TRANSP': 'OPAQUE',
                'UID': '{}@localhost'.format(prev[0]['uuid'])
                } == events[0]

        assert {'DTSTART': '20160613T120000Z',
                'DURATION': 'PT2H',
                'SUMMARY': 'Test #02',
                'TRANSP': 'OPAQUE',
                'UID': '{}@localhost'.format(prev[1]['uuid'])
                } == events[1]

        assert {'DTSTART': '20160614T120000Z',
                'DURATION': 'P2D',
                'SUMMARY': 'Test #03',
                'TRANSP': 'OPAQUE',
                'UID': '{}@localhost'.format(prev[2]['uuid']),
                } == events[2]

    def test_list_calendar_slots__paginate(self):
        self.prepare_accept_3_invitations_3_subscriptions()
        l = self.list_calendar_slots(
                date=iso_dt(dt(2016, 6, 10)),
                delta=iso_td(td(weeks=1)))
        assert l == [['2016-06-12T12:00:00Z', '2016-06-12T12:20:00Z'],
                ['2016-06-13T12:00:00Z', '2016-06-13T14:00:00Z'],
                ['2016-06-14T12:00:00Z', '2016-06-16T12:00:00Z']]
        # following week
        l = self.list_calendar_slots(
                date=iso_dt(dt(2016, 6, 10)+td(weeks=1)),
                delta=iso_td(td(weeks=1)))
        assert l == [['2016-06-19T00:00:00Z', '2016-06-21T00:00:00Z']]
        # the week after
        l = self.list_calendar_slots(
                date=iso_dt(dt(2016, 6, 10)+td(weeks=2)),
                delta=iso_td(td(weeks=1)))
        assert l == []

    def test_list_calendar_soup_ics(self):
        ics = self.list_calendar_soup()
        header, events = self._parse_ics_string(ics, sort_key='DTSTART')

        assert ['BEGIN:VCALENDAR',
                'PRODID:ics.py - http://git.io/lLljaA',
                'VERSION:2.0',
                'END:VCALENDAR'] == header

        assert [] == events

        prev = self.prepare_accept_3_invitations_3_subscriptions()
        ics = self.list_calendar_soup()
        header, events = self._parse_ics_string(ics, sort_key='UID')

        assert [
            'BEGIN:VCALENDAR',
            'PRODID:ics.py - http://git.io/lLljaA',
            'VERSION:2.0',
            ''] == header

        assert {'DTSTART;VALUE=DATE': '20150831',
                'DTEND': '20150902T000000Z',
                'SEQUENCE': '0',
                'DESCRIPTION': 'Visit http://calendarlabs.com/ for any kind of calendar '
                    'needs. Like us on Facebook: http://fb.com/calendarlabs to get '
                    'updates.',
                'STATUS': 'CONFIRMED',
                'TRANSP': 'TRANSPARENT',
                'UID': '0'} == events[0]


        assert {'UID': '1',
                'DTSTART': '20151111T000000Z',
                'DTEND': '20151113T000000Z',
                'TRANSP': 'OPAQUE'} == events[1]

        assert len(events) == 48

