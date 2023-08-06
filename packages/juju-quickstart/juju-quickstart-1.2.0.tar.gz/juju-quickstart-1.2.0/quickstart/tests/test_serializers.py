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

"""Tests for the Juju Quickstart serialization helpers."""

from __future__ import unicode_literals

import unittest

import mock
import yaml

from quickstart import serializers


class TestYamlLoad(unittest.TestCase):

    contents = '{myint: 42, mystring: foo}'

    def test_unicode_strings(self):
        # Strings are returned as unicode objects.
        decoded = serializers.yaml_load(self.contents)
        self.assertEqual(42, decoded['myint'])
        self.assertEqual('foo', decoded['mystring'])
        self.assertIsInstance(decoded['mystring'], unicode)
        for key in decoded:
            self.assertIsInstance(key, unicode, key)

    @mock.patch('quickstart.serializers.yaml.load')
    def test_safe(self, mock_load):
        # The YAML decoder uses a safe loader.
        serializers.yaml_load(self.contents)
        self.assertEqual(self.contents, mock_load.call_args[0][0])
        loader_class = mock_load.call_args[1]['Loader']
        self.assertTrue(issubclass(loader_class, yaml.SafeLoader))


class TestYamlDump(unittest.TestCase):

    data = {'myint': 42, 'mystring': 'foo'}

    def test_block_style(self):
        # Collections are serialized in the block style.
        contents = serializers.yaml_dump(self.data)
        self.assertEqual('myint: 42\nmystring: foo\n', contents)
