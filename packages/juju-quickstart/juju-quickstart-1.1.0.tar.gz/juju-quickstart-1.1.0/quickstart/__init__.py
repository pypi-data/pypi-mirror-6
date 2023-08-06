# This file is part of the Juju Quickstart Plugin, which lets users set up a
# Juju environment in very few steps (https://launchpad.net/juju-quickstart).
# Copyright (C) 2013-2014 Canonical Ltd.
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

"""Juju Quickstart is a Juju plugin which allows for easily setting up a Juju
environment in very few steps. The environment is bootstrapped and set up so
that it can be managed using a Web interface (the Juju GUI).
"""

from __future__ import unicode_literals


VERSION = (1, 1, 0)


def get_version():
    """Return the Juju Quickstart version as a string."""
    return '.'.join(map(unicode, VERSION))
