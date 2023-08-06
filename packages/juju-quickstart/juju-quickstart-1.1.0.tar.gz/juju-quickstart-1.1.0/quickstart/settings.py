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

"""Juju Quickstart settings."""

from __future__ import unicode_literals

import os


# The URL containing information about the last Juju GUI charm version.
CHARMWORLD_API = 'http://manage.jujucharms.com/api/3/charm/precise/juju-gui'

# The default Juju GUI charm URL to use when it is not possible to retrieve it
# from the charmworld API, e.g. due to temporary connection/charmworld errors.
DEFAULT_CHARM_URL = 'cs:precise/juju-gui-83'

# The quickstart app short description.
DESCRIPTION = 'set up a Juju environment (including the GUI) in very few steps'

# The possible values for the environments.yaml default-series field.
JUJU_DEFAULT_SERIES = ('precise', 'quantal', 'raring', 'saucy', 'trusty')

# Retrieve the current juju-core home.
JUJU_HOME = os.getenv('JUJU_HOME', '~/.juju')

# The name of the Juju GUI charm.
JUJU_GUI_CHARM_NAME = 'juju-gui'

# The name of the Juju GUI service.
JUJU_GUI_SERVICE_NAME = JUJU_GUI_CHARM_NAME

# The set of series supported by the Juju GUI charm.
JUJU_GUI_SUPPORTED_SERIES = ('precise',)

# The preferred series for the Juju GUI charm.  It will be the newest,
# assuming our naming convention holds.
JUJU_GUI_PREFERRED_SERIES = sorted(JUJU_GUI_SUPPORTED_SERIES).pop()

# The minimum Juju GUI charm revision supporting bundle deployments.
MINIMUM_CHARM_REVISION_FOR_BUNDLES = 80
