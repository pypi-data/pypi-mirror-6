# This file is part of the Juju Quickstart Plugin, which lets users set up a
# Juju environment in very few steps (https://launchpad.net/juju-quickstart).
# Copyright (C) 2014 Canonical Ltd.
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Affero General Public License version 3, as published by
# the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranties of MERCHANTABILITY,
# SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Tests for the Juju Quickstart environments watching utilities."""

from __future__ import unicode_literals

import unittest

import mock

from quickstart import watchers
from quickstart.tests import helpers


class TestParseMachineChange(helpers.ValueErrorTestsMixin, unittest.TestCase):

    def test_machine_removed(self):
        # A ValueError is raised if the change represents a machine removal.
        data = {'Id': '1', 'Status': 'started'}
        with self.assert_value_error('machine 1 unexpectedly removed'):
            watchers.parse_machine_change('remove', data, '')

    def test_machine_error(self):
        # A ValueError is raised if the machine is in an error state.
        data = {'Id': '1', 'Status': 'error', 'StatusInfo': 'bad wolf'}
        expected_error = 'machine 1 is in an error state: error: bad wolf'
        with self.assert_value_error(expected_error):
            watchers.parse_machine_change('change', data, '')

    @helpers.mock_print
    def test_pending_status_notified(self, mock_print):
        # A message is printed to stdout when the machine changes its status
        # to "pending". The new status is also returned by the function.
        data = {'Id': '1', 'Status': 'pending'}
        status = watchers.parse_machine_change('change', data, '')
        self.assertEqual('pending', status)
        mock_print.assert_called_once_with('machine 1 provisioning is pending')

    @helpers.mock_print
    def test_started_status_notified(self, mock_print):
        # A message is printed to stdout when the machine changes its status
        # to "started". The new status is also returned by the function.
        data = {'Id': '42', 'Status': 'started'}
        status = watchers.parse_machine_change('change', data, 'pending')
        self.assertEqual('started', status)
        mock_print.assert_called_once_with('machine 42 is started')

    @helpers.mock_print
    def test_status_not_changed(self, mock_print):
        # If the status in the machine change and the given current status are
        # the same value, nothing is printed and the status is returned.
        data = {'Id': '47', 'Status': 'pending'}
        status = watchers.parse_machine_change('change', data, 'pending')
        self.assertEqual('pending', status)
        self.assertFalse(mock_print.called)


class TestParseUnitChange(helpers.ValueErrorTestsMixin, unittest.TestCase):

    def test_unit_removed(self):
        # A ValueError is raised if the change represents a unit removal.
        data = {'Name': 'django/42', 'Status': 'started'}
        with self.assert_value_error('django/42 unexpectedly removed'):
            # The last two arguments are the current status and address.
            watchers.parse_unit_change('remove', data, '', '')

    def test_unit_error(self):
        # A ValueError is raised if the unit is in an error state.
        data = {
            'Name': 'django/0',
            'Status': 'start error',
            'StatusInfo': 'bad wolf',
        }
        expected_error = 'django/0 is in an error state: start error: bad wolf'
        with self.assert_value_error(expected_error):
            # The last two arguments are the current status and address.
            watchers.parse_unit_change('change', data, '', '')

    @helpers.mock_print
    def test_address_notified(self, mock_print):
        # A message is printed to stdout when the unit obtains a public
        # address. The function returns the status, the new address and the
        # machine identifier.
        data = {
            'Name': 'haproxy/2',
            'Status': 'pending',
            'PublicAddress': 'haproxy2.example.com',
            'MachineId': '42',
        }
        status, address, machine_id = watchers.parse_unit_change(
            'change', data, 'pending', '')
        self.assertEqual('pending', status)
        self.assertEqual('haproxy2.example.com', address)
        self.assertEqual('42', machine_id)
        mock_print.assert_called_once_with(
            'setting up haproxy/2 on haproxy2.example.com')

    @helpers.mock_print
    def test_pending_status_notified(self, mock_print):
        # A message is printed to stdout when the unit changes its status to
        # "pending". The function returns the new status, the address and the
        # machine identifier. The last two values are empty strings if the unit
        # has not yet been assigned to a machine.
        data = {'Name': 'django/1', 'Status': 'pending', 'PublicAddress': ''}
        # The last two arguments are the current status and address.
        status, address, machine_id = watchers.parse_unit_change(
            'change', data, '', '')
        self.assertEqual('pending', status)
        self.assertEqual('', address)
        self.assertEqual('', machine_id)
        mock_print.assert_called_once_with('django/1 deployment is pending')

    @helpers.mock_print
    def test_installed_status_notified(self, mock_print):
        # A message is printed to stdout when the unit changes its status to
        # "installed". The function returns the new status, the address and the
        # machine identifier.
        data = {
            'Name': 'django/42',
            'Status': 'installed',
            'PublicAddress': 'django42.example.com',
            'MachineId': '1',
        }
        status, address, machine_id = watchers.parse_unit_change(
            'change', data, 'pending', 'django42.example.com')
        self.assertEqual('installed', status)
        self.assertEqual('django42.example.com', address)
        self.assertEqual('1', machine_id)
        mock_print.assert_called_once_with('django/42 is installed')

    @helpers.mock_print
    def test_started_status_notified(self, mock_print):
        # A message is printed to stdout when the unit changes its status to
        # "started". The function returns the new status, the address and the
        # machine identifier.
        data = {
            'Name': 'wordpress/0',
            'Status': 'started',
            'PublicAddress': 'wordpress0.example.com',
            'MachineId': '0',
        }
        status, address, machine_id = watchers.parse_unit_change(
            'change', data, '', 'wordpress0.example.com')
        self.assertEqual('started', status)
        self.assertEqual('wordpress0.example.com', address)
        self.assertEqual('0', machine_id)
        mock_print.assert_called_once_with('wordpress/0 is ready on machine 0')

    @helpers.mock_print
    def test_both_status_and_address_notified(self, mock_print):
        # Both status and public address changes are notified if required.
        data = {
            'Name': 'django/0',
            'Status': 'started',
            'PublicAddress': 'django42.example.com',
            'MachineId': '0',
        }
        # The last two arguments are the current status and address.
        watchers.parse_unit_change('change', data, '', '')
        self.assertEqual(2, mock_print.call_count)
        mock_print.assert_has_calls([
            mock.call('setting up django/0 on django42.example.com'),
            mock.call('django/0 is ready on machine 0'),
        ])

    @helpers.mock_print
    def test_status_not_changed(self, mock_print):
        # If the status in the unit change and the given current status are the
        # same value, nothing is printed and the current values are returned.
        data = {'Name': 'django/1', 'Status': 'pending', 'PublicAddress': ''}
        status, address, machine_id = watchers.parse_unit_change(
            'change', data, 'pending', '')
        self.assertEqual('pending', status)
        self.assertEqual('', address)
        self.assertEqual('', machine_id)
        self.assertFalse(mock_print.called)


class TestUnitMachineChanges(unittest.TestCase):

    def test_unit_changes_found(self):
        # Unit changes are correctly found and returned.
        data1 = {'Name': 'django/42', 'Status': 'started'}
        data2 = {'Name': 'django/47', 'Status': 'pending'}
        changeset = [('unit', 'change', data1), ('unit', 'remove', data2)]
        expected_unit_changes = [('change', data1), ('remove', data2)]
        self.assertEqual(
            (expected_unit_changes, []),
            watchers.unit_machine_changes(changeset))

    def test_machine_changes_found(self):
        # Machine changes are correctly found and returned.
        data1 = {'Id': '0', 'Status': 'started'}
        data2 = {'Id': '1', 'Status': 'error'}
        changeset = [
            ('machine', 'change', data1),
            ('machine', 'remove', data2),
        ]
        expected_machine_changes = [('change', data1), ('remove', data2)]
        self.assertEqual(
            ([], expected_machine_changes),
            watchers.unit_machine_changes(changeset))

    def test_unit_and_machine_changes_found(self):
        # Changes to unit and machines are reordered, grouped and returned.
        machine_data1 = {'Id': '0', 'Status': 'started'}
        machine_data2 = {'Id': '42', 'Status': 'started'}
        unit_data1 = {'Name': 'django/42', 'Status': 'error'}
        unit_data2 = {'Name': 'haproxy/47', 'Status': 'pending'}
        unit_data3 = {'Name': 'wordpress/0', 'Status': 'installed'}
        changeset = [
            ('machine', 'change', machine_data1),
            ('unit', 'change', unit_data1),
            ('machine', 'remove', machine_data2),
            ('unit', 'change', unit_data2),
            ('unit', 'remove', unit_data3),
        ]
        expected_unit_changes = [
            ('change', unit_data1),
            ('change', unit_data2),
            ('remove', unit_data3),
        ]
        expected_machine_changes = [
            ('change', machine_data1),
            ('remove', machine_data2),
        ]
        self.assertEqual(
            (expected_unit_changes, expected_machine_changes),
            watchers.unit_machine_changes(changeset))

    def test_other_entities(self):
        # Changes to other entities (like services) are ignored.
        machine_data = {'Id': '0', 'Status': 'started'}
        unit_data = {'Name': 'django/42', 'Status': 'error'}
        changeset = [
            ('machine', 'change', machine_data),
            ('service', 'change', {'Name': 'django', 'Status': 'pending'}),
            ('unit', 'change', unit_data),
            ('service', 'remove', {'Name': 'haproxy', 'Status': 'started'}),
        ]
        expected_changes = (
            [('change', unit_data)],
            [('change', machine_data)],
        )
        self.assertEqual(
            expected_changes, watchers.unit_machine_changes(changeset))

    def test_empty_changeset(self):
        # Two empty lists are returned if the changeset is empty.
        # This should never occur in the real world, but it's tested here to
        # demonstrate this function behavior.
        self.assertEqual(([], []), watchers.unit_machine_changes([]))
