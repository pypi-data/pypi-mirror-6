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

"""Juju Quickstart utilities for watching Juju environments."""

from __future__ import (
    print_function,
    unicode_literals,
)


def parse_machine_change(action, data, current_status):
    """Parse the given machine change.

    The change is represented by the given action/data pair.
    Also receive the last known machine status, which can be an empty string
    if the information is unknown.

    Output a human readable message each time a relevant change is found.

    Return the machine status.
    Raise a ValueError if the machine is removed or in an error state.
    """
    machine_id = data['Id']
    status = data['Status']
    # Exit with an error if the machine is removed.
    if action == 'remove':
        msg = 'machine {} unexpectedly removed'.format(machine_id)
        raise ValueError(msg.encode('utf-8'))
    if 'error' in status:
        msg = 'machine {} is in an error state: {}: {}'.format(
            machine_id, status, data['StatusInfo'])
        raise ValueError(msg.encode('utf-8'))
    # Notify status changes.
    if status != current_status:
        if status == 'pending':
            print('machine {} provisioning is pending'.format(
                machine_id))
        elif status == 'started':
            print('machine {} is started'.format(machine_id))
    return status


def parse_unit_change(action, data, current_status, address):
    """Parse the given unit change.

    The change is represented by the given action/data pair.
    Also receive the last known unit status and address, which can be empty
    strings if those pieces of information are unknown.

    Output a human readable message each time a relevant change is found.

    Return the unit status, address and machine identifier.
    Raise a ValueError if the service unit is removed or in an error state.
    """
    unit_name = data['Name']
    # Exit with an error if the unit is removed.
    if action == 'remove':
        msg = '{} unexpectedly removed'.format(unit_name)
        raise ValueError(msg.encode('utf-8'))
    # Exit with an error if the unit is in an error state.
    status = data['Status']
    if 'error' in status:
        msg = '{} is in an error state: {}: {}'.format(
            unit_name, status, data['StatusInfo'])
        raise ValueError(msg.encode('utf-8'))
    # Notify when the unit becomes reachable.
    if not address:
        address = data['PublicAddress']
        if address:
            print('setting up {} on {}'.format(unit_name, address))
    # Notify status changes.
    if status != current_status:
        if status == 'pending':
            print('{} deployment is pending'.format(unit_name))
        elif status == 'installed':
            print('{} is installed'.format(unit_name))
        elif address and status == 'started':
            print('{} is ready on machine {}'.format(
                unit_name, data['MachineId']))
    return status, address, data.get('MachineId', '')


def unit_machine_changes(changeset):
    """Parse the changeset and return the units and machines related changes.

    Changes to units and machines are grouped into two lists, e.g.:

        unit_changes, machine_changes = unit_machine_changes(changeset)

    Each list includes (action, data) tuples, in which:
        - action is he change type (e.g. "change", "remove");
        - data is the actual information about the changed entity (as a dict).

    This function is intended to be used as a processor callable for the
    watch_changes method of quickstart.juju.Environment.
    """
    unit_changes = []
    machine_changes = []
    for entity, action, data in changeset:
        if entity == 'unit':
            unit_changes.append((action, data))
        elif entity == 'machine':
            machine_changes.append((action, data))
    return unit_changes, machine_changes
