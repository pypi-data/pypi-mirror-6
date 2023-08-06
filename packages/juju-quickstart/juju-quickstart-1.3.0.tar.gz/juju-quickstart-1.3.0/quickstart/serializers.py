# This file is part of the Juju Quickstart Plugin, which lets users set up a
# Juju environment in very few steps (https://launchpad.net/juju-quickstart).
# Copyright (C) 2013 Canonical Ltd.
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

"""Juju Quickstart functions for serializing data structures."""

from __future__ import unicode_literals

import yaml


def yaml_load(stream):
    """Parse the YAML document in stream.

    The stream argument can be a file like object or a string content.

    Produce and return the corresponding Python object, returning strings
    as unicode objects.
    """
    # See <http://stackoverflow.com/questions/2890146/
    # how-to-force-pyyaml-to-load-strings-as-unicode-objects>.
    loader_class = type(b'UnicodeLoader', (yaml.SafeLoader,), {})
    loader_class.add_constructor(
        'tag:yaml.org,2002:str',
        lambda loader, node: loader.construct_scalar(node))
    return yaml.load(stream, Loader=loader_class)


def yaml_dump(data, stream=None):
    """Serialize a Python object into a YAML stream.

    If stream is None, return the produced string instead.
    Always serialize collections in the block style.
    """
    return yaml.safe_dump(data, stream, default_flow_style=False)
