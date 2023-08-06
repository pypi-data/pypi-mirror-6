import os
import sys

pytrac_root = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..')
sys.path.insert(0, pytrac_root)

import pytest
from mock import Mock
import datetime

from pytrac import Ticket


class TestTicket(object):

    def setup_class(self):
        server = Mock()
        self.ticket = Ticket(server)

    def testSearchWithAllParams(self):
        self.ticket.search(summary='test_summary', owner='someowner', status='new')
        self.ticket.api.query.assert_called_with('summary~=test_summary&owner=someowner&status=new&max=0')


class TestUpdateTicket(object):

    ticket_id = 1

    def setup_class(self):
        server = Mock()
        self.timestamp = datetime.datetime.now()
        server.ticket.get.return_value = [self.ticket_id,
                                          self.timestamp,
                                          self.timestamp,
                                          {'_ts': self.timestamp,
                                           'action': 'leave'}]
        server.ticket.update.return_value = [self.ticket_id,
                                             self.timestamp,
                                             self.timestamp,
                                             {'_ts': self.timestamp,
                                              'action': 'leave'}]
        server.ticket.getActions.return_value = [
            ['leave', 'leave', '.', []],
            ['resolve', 'resolve', "The resolution will be set. Next status will be 'closed'.",
                [['action_resolve_resolve_resolution', 'fixed',
                    ['fixed', 'worksforme']]]]]
        self.ticket = Ticket(server)

    def testComment(self):
        self.ticket.comment(self.ticket_id, "some comment")
        self.ticket.api.update.assert_called_with(
            self.ticket_id,
            comment="some comment",
            attrs={'action': 'leave', '_ts': self.timestamp},
            notify=True)

    def testClose(self):
        self.ticket.close(self.ticket_id, "some comment")
        self.ticket.api.update.assert_called_with(
            self.ticket_id,
            comment="some comment",
            attrs={'action': 'resolve',
                   '_ts': self.timestamp,
                   'action_resolve_resolve_resolution': 'fixed',
                   'status': 'closed'},
            notify=True)

if __name__ == '__main__':
    pytest.main(__file__)
