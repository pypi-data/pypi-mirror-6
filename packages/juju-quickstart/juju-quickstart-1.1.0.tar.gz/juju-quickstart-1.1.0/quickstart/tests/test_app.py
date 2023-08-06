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

"""Tests for the Juju Quickstart base application functions."""

from __future__ import unicode_literals

from contextlib import contextmanager
import json
import os
import unittest

import jujuclient
import mock
import yaml

from quickstart import (
    app,
    settings,
)
from quickstart.tests import helpers


class TestProgramExit(unittest.TestCase):

    def test_string_representation(self):
        # The error is properly represented as a string.
        exception = app.ProgramExit('bad wolf')
        self.assertEqual('juju-quickstart: error: bad wolf', bytes(exception))


class ProgramExitTestsMixin(object):
    """Set up some base methods for testing functions raising ProgramExit."""

    @contextmanager
    def assert_program_exit(self, error):
        """Ensure a ProgramExit is raised in the context block.

        Also check that the exception includes the expected error message.
        """
        with self.assertRaises(app.ProgramExit) as context_manager:
            yield
        expected = 'juju-quickstart: error: {}'.format(error)
        self.assertEqual(expected, bytes(context_manager.exception))

    def make_env_error(self, message):
        """Create and return a jujuclient.EnvError with the given message."""
        return jujuclient.EnvError({'Error': message})


@helpers.mock_print
class TestEnsureDependencies(
        helpers.CallTestsMixin, ProgramExitTestsMixin, unittest.TestCase):

    add_repository = '/usr/bin/add-apt-repository'
    apt_get = '/usr/bin/apt-get'

    def call_ensure_dependencies(self, call_effects):
        with self.patch_multiple_calls(call_effects) as mock_call:
            app.ensure_dependencies()
        return mock_call

    def test_success_install(self, mock_print):
        # All the missing packages are installed from the PPA.
        side_effects = (
            (127, '', 'no juju'),  # Check the juju command.
            (127, '', 'no lxc'),  # Check the lxc-ls command.
            (0, 'saucy', ''),  # Retrieve the Ubuntu release codename.
            (0, 'install add repo', ''),  # Install add-apt-repository.
            (0, 'add repo', ''),  # Add the juju stable repository.
            (0, 'update', ''),  # Update the repository with new sources.
            (0, 'install', ''),  # Install missing packages.
        )
        mock_call = self.call_ensure_dependencies(side_effects)
        self.assertEqual(len(side_effects), mock_call.call_count)
        mock_call.assert_has_calls([
            mock.call('/usr/bin/juju', 'version'),
            mock.call('/usr/bin/lxc-ls'),
            mock.call('lsb_release', '-cs'),
            mock.call('sudo', self.apt_get, 'install', '-y',
                      'software-properties-common'),
            mock.call('sudo', self.add_repository, '-y', 'ppa:juju/stable'),
            mock.call('sudo', self.apt_get, 'update'),
            mock.call('sudo', self.apt_get, 'install', '-y',
                      'juju-core', 'lxc', 'mongodb-server'),
        ])
        mock_print.assert_has_calls([
            mock.call('sudo privileges are required for PPA installation'),
            mock.call('installing the following packages: juju-core, '
                      'lxc, mongodb-server (this can take a while)'),
            mock.call('sudo privileges will be used for package installation'),
        ])

    def test_success_no_install(self, mock_print):
        # There is no need to install packages/PPAs if everything is already
        # set up.
        side_effects = (
            (0, '1.16', ''),  # Check the juju command.
            (0, '', ''),  # Check the lxc-ls command.
            # The remaining call should be ignored.
            (1, '', 'not ignored'),
        )
        mock_call = self.call_ensure_dependencies(side_effects)
        self.assertEqual(2, mock_call.call_count)
        self.assertFalse(mock_print.called)

    def test_success_partial_install(self, mock_print):
        # One missing installation is correctly handled.
        side_effects = (
            (0, '1.16', ''),  # Check the juju command.
            (127, '', 'no lxc'),  # Check the lxc-ls command.
            (0, 'saucy', ''),  # Retrieve the Ubuntu release codename.
            (0, 'install add repo', ''),  # Install add-apt-repository.
            (0, 'add repo', ''),  # Add the juju stable repository.
            (0, 'update', ''),  # Update the repository with new sources.
            (0, 'install', ''),  # Install missing packages.
        )
        mock_call = self.call_ensure_dependencies(side_effects)
        self.assertEqual(len(side_effects), mock_call.call_count)
        mock_call.assert_has_calls([
            mock.call('/usr/bin/juju', 'version'),
            mock.call('/usr/bin/lxc-ls'),
            mock.call('lsb_release', '-cs'),
            mock.call('sudo', self.apt_get, 'install', '-y',
                      'software-properties-common'),
            mock.call('sudo', self.add_repository, '-y', 'ppa:juju/stable'),
            mock.call('sudo', self.apt_get, 'update'),
            mock.call('sudo', self.apt_get, 'install', '-y',
                      'lxc', 'mongodb-server'),
        ])
        mock_print.assert_has_calls([
            mock.call('sudo privileges are required for PPA installation'),
            mock.call('installing the following packages: '
                      'lxc, mongodb-server (this can take a while)'),
            mock.call('sudo privileges will be used for package installation'),
        ])

    def test_add_repository_failure(self, mock_print):
        # A ProgramExit is raised if the PPA is not successfully installed.
        side_effects = (
            (127, '', 'no juju'),  # Check the juju command.
            (127, '', 'no lxc'),  # Check the lxc-ls command.
            (0, 'saucy', ''),  # Retrieve the Ubuntu release codename.
            (0, 'install add repo', ''),  # Install add-apt-repository.
            (1, '', 'add repo error'),  # Add the juju stable repository.
        )
        with self.assert_program_exit('add repo error'):
            mock_call = self.call_ensure_dependencies(side_effects)
            self.assertEqual(3, mock_call.call_count)

    def test_install_failure(self, mock_print):
        # A ProgramExit is raised if the packages installation fails.
        side_effects = (
            (127, '', 'no juju'),  # Check the juju command.
            (127, '', 'no lxc'),  # Check the lxc-ls command.
            (0, 'saucy', ''),  # Retrieve the Ubuntu release codename.
            (0, 'install add repo', ''),  # Install add-apt-repository.
            (0, 'add repo', ''),  # Add the juju stable repository.
            (0, 'update', ''),  # Update the repository with new sources.
            (1, '', 'install error'),  # Install missing packages.
        )
        with self.assert_program_exit('install error'):
            mock_call = self.call_ensure_dependencies(side_effects)
            self.assertEqual(3, mock_call.call_count)


@helpers.mock_print
class TestEnsureSSHKeys(
        helpers.CallTestsMixin, ProgramExitTestsMixin, unittest.TestCase):

    print_msg = 'Warning: No SSH keys were found in ~/.ssh\n\nTo proceed ' \
                'and generate keys, quickstart can\n\n[a] automatically ' \
                'create keys for you\n[m] provide commands to manually ' \
                'create your keys\n\nNote:\nssh-keygen will prompt you for ' \
                'an optional passphrase to generate your key for\nyou. ' \
                'Quickstart does not store it.\n'
    exit_msg = 'If you would like to create the keys yourself, please run ' \
               'this command, follow its instructions, and then re-run ' \
               'quickstart:\n\n  ssh-keygen -b 4096 -t rsa'

    def patch_check_ssh_keys(self, return_value=False):
        mock_ = mock.Mock(return_value=return_value)
        return mock.patch('quickstart.app.check_ssh_keys', mock_)

    def patch_raw_input(self, return_value='C'):
        mock_ = mock.Mock(return_value=return_value)
        return mock.patch('__builtin__.raw_input', mock_)

    def patch_start_ssh_agent(self, return_value=False, side_effect=None):
        mock_ = mock.Mock(return_value=return_value, side_effect=side_effect)
        return mock.patch('quickstart.utils.start_ssh_agent', mock_)

    def test_success(self, mock_print):
        with self.patch_check_ssh_keys(return_value=True) as mock_check:
            with self.patch_start_ssh_agent(return_value=True):
                app.ensure_ssh_keys()
        self.assertEqual(1, mock_check.call_count)

    def test_error_starting_agent(self, mock_print):
        with self.assert_program_exit('foo'):
            with self.patch_check_ssh_keys():
                with self.patch_start_ssh_agent(side_effect=OSError('foo')):
                    app.ensure_ssh_keys()

    def test_extant_agent_returns(self, mock_print):
        with self.patch_check_ssh_keys(True):
            with self.patch_start_ssh_agent(
                    side_effect=OSError('foo')) as mock_ssa:
                app.ensure_ssh_keys()
        self.assertFalse(mock_ssa.called)

    def test_successful_agent_start(self, mock_print):
        mock_check_ssh_keys = mock.Mock(side_effect=(False, True))
        with mock.patch('quickstart.app.check_ssh_keys', mock_check_ssh_keys):
            with self.patch_start_ssh_agent(return_value=True):
                app.ensure_ssh_keys()
        self.assertFalse(mock_print.called)

    def test_failure_no_keygen(self, mock_print):
        with mock.patch('sys.exit') as mock_exit:
            with self.patch_check_ssh_keys() as mock_check:
                with self.patch_start_ssh_agent(return_value=True):
                    with self.patch_raw_input() as mock_raw_input:
                        app.ensure_ssh_keys()
        self.assertTrue(mock_check.called)
        mock_print.assert_has_calls([mock.call(self.print_msg)])
        self.assertTrue(mock_raw_input.called)
        mock_exit.assert_called_once_with(self.exit_msg)

    def test_failure_no_keygen_interrupt(self, mock_print):
        with mock.patch('sys.exit') as mock_exit:
            with self.patch_check_ssh_keys() as mock_check:
                with self.patch_start_ssh_agent(return_value=True):
                    with mock.patch('__builtin__.raw_input',
                                    side_effect=KeyboardInterrupt) \
                            as mock_raw_input:
                        app.ensure_ssh_keys()
        self.assertTrue(mock_check.called)
        mock_print.assert_has_calls([mock.call(self.print_msg)])
        self.assertTrue(mock_raw_input.called)
        mock_exit.assert_called_once_with(self.exit_msg)

    def test_failure_with_keygen(self, mock_print):
        with self.patch_check_ssh_keys() as mock_check:
            with self.patch_start_ssh_agent(return_value=True):
                with self.patch_raw_input(return_value='A') as mock_raw_input:
                    with mock.patch('quickstart.app.create_ssh_keys') \
                            as mock_create_ssh_keys:
                        app.ensure_ssh_keys()
        self.assertTrue(mock_check.called)
        mock_print.assert_has_calls([mock.call(self.print_msg)])
        self.assertTrue(mock_raw_input.called)
        self.assertTrue(mock_create_ssh_keys.called)

    def test_failure_with_watch(self, mock_print):
        with self.patch_check_ssh_keys() as mock_check:
            with self.patch_start_ssh_agent(return_value=True):
                with self.patch_raw_input(return_value='M') as mock_raw_input:
                    with mock.patch('quickstart.app.watch_for_ssh_keys') \
                            as mock_watch_for_ssh_keys:
                        app.ensure_ssh_keys()
        self.assertTrue(mock_check.called)
        mock_print.assert_has_calls([mock.call(self.print_msg)])
        self.assertTrue(mock_raw_input.called)
        self.assertTrue(mock_watch_for_ssh_keys.called)


class TestCheckSSHKeys(
        helpers.CallTestsMixin, ProgramExitTestsMixin, unittest.TestCase):

    def test_keys_and_agent(self):
        with self.patch_call(retcode=0) as mock_call:
            have_keys = app.check_ssh_keys()
        mock_call.assert_called_once_with('/usr/bin/ssh-add', '-l')
        self.assertTrue(have_keys)

    def test_agent_no_keys_success(self):
        side_effects = (
            (1, 'The agent has no identities.\n', ''),
            (0, '', ''),
        )
        with self.patch_multiple_calls(side_effects) as mock_call:
            have_keys = app.check_ssh_keys()
        mock_call.assert_has_calls([
            mock.call('/usr/bin/ssh-add', '-l'),
            mock.call('/usr/bin/ssh-add'),
        ])
        self.assertTrue(have_keys)

    def test_agent_no_keys_failure(self):
        side_effects = (
            (1, 'The agent has no identities.\n', ''),
            (1, 'Still no identities...', ''),
        )
        with self.patch_multiple_calls(side_effects) as mock_call:
            have_keys = app.check_ssh_keys()
        mock_call.assert_has_calls([
            mock.call('/usr/bin/ssh-add', '-l'),
            mock.call('/usr/bin/ssh-add'),
        ])
        self.assertFalse(have_keys)

    def test_agent_bad_keys(self):
        side_effects = (
            (1, 'The agent has no identities.\n', ''),
            (2, '', 'Oh no!'),
        )
        msg = 'error attempting to add ssh keys! Oh no!'
        with self.assert_program_exit(msg):
            with self.patch_multiple_calls(side_effects) as mock_call:
                app.check_ssh_keys()
        mock_call.assert_has_calls([
            mock.call('/usr/bin/ssh-add', '-l'),
            mock.call('/usr/bin/ssh-add'),
        ])

    def test_no_agent(self):
        with self.patch_call(retcode=2) as mock_call:
            have_keys = app.check_ssh_keys()
        mock_call.assert_called_once_with('/usr/bin/ssh-add', '-l')
        self.assertFalse(have_keys)


@mock.patch('time.sleep')
@helpers.mock_print
class TestWatchForSSHKeys(helpers.CallTestsMixin, unittest.TestCase):

    def test_watch(self, mock_print, mock_sleep):
        with mock.patch('quickstart.app.check_ssh_keys',
                        mock.Mock(side_effect=(False, True))):
            app.watch_for_ssh_keys()
        mock_print.assert_has_calls([
            mock.call('Please run this command in another terminal or window '
                      'and follow the\ninstructions it produces; quickstart '
                      'will continue when keys are\ngenerated, or ^C to quit.'
                      '\n\n  ssh-keygen -b 4096 -t rsa\n\nWaiting...'),
            mock.call('.', end=''),
        ])
        mock_sleep.assert_called_once_with(3)

    def test_cancel(self, mock_print, mock_sleep):
        with mock.patch('quickstart.app.check_ssh_keys',
                        mock.Mock(side_effect=KeyboardInterrupt)):
            with mock.patch('sys.exit') as mock_exit:
                app.watch_for_ssh_keys()
        mock_print.assert_has_calls([
            mock.call('Please run this command in another terminal or window '
                      'and follow the\ninstructions it produces; quickstart '
                      'will continue when keys are\ngenerated, or ^C to quit.'
                      '\n\n  ssh-keygen -b 4096 -t rsa\n\nWaiting...'),
        ])
        mock_exit.assert_called_once_with('\nquitting')


@helpers.mock_print
class TestCreateSSHKeys(
        helpers.CallTestsMixin, ProgramExitTestsMixin, unittest.TestCase):

    def test_success(self, mock_print):
        key_file = os.path.join(os.path.expanduser('~'), '.ssh', 'id_rsa')
        with self.patch_call(retcode=0) as mock_call:
            app.create_ssh_keys()
        mock_call.assert_has_calls([
            mock.call('/usr/bin/ssh-keygen',
                      '-q', '-b', '4096', '-t', 'rsa',
                      '-C',
                      'Generated with Juju Quickstart',
                      '-f', key_file),
            mock.call('/usr/bin/ssh-add')
        ])
        mock_print.assert_called_with('a new ssh key was generated in {}'
                                      .format(key_file))

    def test_failure(self, mock_print):
        with self.assert_program_exit('error generating ssh key!  Oh no!'):
            with self.patch_call(retcode=1, error='Oh no!') as mock_call:
                app.create_ssh_keys()
        self.assertTrue(mock_call.called)
        with self.assert_program_exit('error adding key to agent!  Oh no!'):
            side_effects = (
                (0, '', ''),
                (1, '', 'Oh no!'),
            )
            with self.patch_multiple_calls(side_effects) as mock_call:
                app.create_ssh_keys()
        self.assertTrue(mock_call.called)


@helpers.mock_print
class TestBootstrapRequiresSudo(ProgramExitTestsMixin, unittest.TestCase):

    sudo_message = 'sudo privileges required to bootstrap the environment'

    def patch_get_juju_version(self, return_value):
        """Patch the quickstart.utils.get_juju_version function."""
        if isinstance(return_value, Exception):
            mock_get_juju_version = mock.Mock(side_effect=return_value)
        else:
            mock_get_juju_version = mock.Mock(return_value=return_value)
        return mock.patch(
            'quickstart.utils.get_juju_version', mock_get_juju_version)

    def test_not_local(self, mock_print):
        # Sudo privileges are never required for non-local environments.
        self.assertFalse(app.bootstrap_requires_sudo(False))

    def test_sudo_required(self, mock_print):
        # Sudo privileges are required if the Juju version is < 1.17.2.
        versions = [(0, 7, 9), (1, 0, 0), (1, 16, 42), (1, 17, 0), (1, 17, 1)]
        for version in versions:
            with self.patch_get_juju_version(version):
                requires_sudo = app.bootstrap_requires_sudo(True)
            self.assertTrue(requires_sudo, version)
            # On local environments the "sudo privileges required" message is
            # always printed.
            mock_print.assert_called_once_with(self.sudo_message)
            mock_print.reset_mock()

    def test_sudo_not_required(self, mock_print):
        # Sudo privileges are not required if the Juju version is >= 1.17.2.
        versions = [
            (1, 17, 2), (1, 17, 10), (1, 18, 0), (1, 18, 2), (2, 16, 1)]
        for version in versions:
            with self.patch_get_juju_version(version):
                requires_sudo = app.bootstrap_requires_sudo(True)
            self.assertFalse(requires_sudo, version)
            # On local environments the "sudo privileges required" message is
            # always printed.
            mock_print.assert_called_once_with(self.sudo_message)
            mock_print.reset_mock()

    def test_invalid_version(self, mock_print):
        # A ProgramExit is raised if the Juju version is not valid.
        with self.patch_get_juju_version(ValueError(b'bad wolf')):
            with self.assert_program_exit('bad wolf'):
                app.bootstrap_requires_sudo(True)


@helpers.mock_print
class TestBootstrap(
        helpers.CallTestsMixin, ProgramExitTestsMixin, unittest.TestCase):

    env_name = 'my-juju-env'
    juju = '/usr/bin/juju'
    status_message = 'retrieving the environment status'

    def make_status_output(self, agent_state, series='hoary'):
        """Create and return a YAML status output."""
        return yaml.safe_dump({
            'machines': {'0': {'agent-state': agent_state,
                               'series': series}},
        })

    def make_status_calls(self, number):
        """Return a list containing the given number of status calls."""
        call = mock.call(
            self.juju, 'status', '-e', self.env_name, '--format', 'yaml')
        return [call for _ in range(number)]

    def make_side_effects(self):
        """Return the minimum number of side effects for a successful call."""
        return [
            (0, '', ''),  # Add a bootstrap call.
            (0, self.make_status_output('started'), ''),  # Add a status call.
        ]

    def assert_status_retried(self, side_effects):
        """Ensure the "juju status" command is retried several times.

        Receive the list of side effects the mock status call will return.
        """
        with self.patch_multiple_calls(side_effects) as mock_call:
            app.bootstrap(self.env_name)
        mock_call.assert_has_calls([
            mock.call(self.juju, 'bootstrap', '-e', self.env_name),
        ] + self.make_status_calls(5))

    def test_success(self, mock_print):
        # The environment is successfully bootstrapped.
        with self.patch_multiple_calls(self.make_side_effects()) as mock_call:
            already_bootstrapped, series = app.bootstrap(self.env_name)
        self.assertFalse(already_bootstrapped)
        self.assertEqual(series, 'hoary')
        mock_call.assert_has_calls([
            mock.call(self.juju, 'bootstrap', '-e', self.env_name),
        ] + self.make_status_calls(1))
        mock_print.assert_called_once_with(self.status_message)

    def test_success_local_provider(self, mock_print):
        # The environment is bootstrapped with sudo using the local provider.
        with self.patch_multiple_calls(self.make_side_effects()) as mock_call:
            already_bootstrapped, series = app.bootstrap(
                self.env_name, requires_sudo=True)
        self.assertFalse(already_bootstrapped)
        self.assertEqual(series, 'hoary')
        mock_call.assert_has_calls([
            mock.call('sudo', self.juju, 'bootstrap', '-e', self.env_name),
        ] + self.make_status_calls(1))
        mock_print.assert_called_once_with(self.status_message)

    def test_success_debug(self, mock_print):
        # The environment is successfully bootstrapped in debug mode.
        with self.patch_multiple_calls(self.make_side_effects()) as mock_call:
            already_bootstrapped, series = app.bootstrap(
                self.env_name, debug=True)
        self.assertFalse(already_bootstrapped)
        self.assertEqual(series, 'hoary')
        mock_call.assert_has_calls([
            mock.call(self.juju, 'bootstrap', '-e', self.env_name, '--debug'),
        ] + self.make_status_calls(1))

    def test_already_bootstrapped(self, mock_print):
        # The function succeeds and returns True if the environment is already
        # bootstrapped.
        side_effects = [
            (1, '', '***environment is already bootstrapped**'),
            (0, self.make_status_output('started', 'precise'), ''),
        ]
        with self.patch_multiple_calls(side_effects) as mock_call:
            already_bootstrapped, series = app.bootstrap(self.env_name)
        self.assertTrue(already_bootstrapped)
        self.assertEqual(series, 'precise')
        mock_call.assert_has_calls([
            mock.call(self.juju, 'bootstrap', '-e', self.env_name),
        ] + self.make_status_calls(1))
        existing_message = 'reusing the already bootstrapped {} environment'
        mock_print.assert_has_calls([
            mock.call(existing_message.format(self.env_name)),
            mock.call(self.status_message),
        ])

    def test_bootstrap_failure(self, mock_print):
        # A ProgramExit is raised if an error occurs while bootstrapping.
        with self.patch_call(retcode=1, error='bad wolf') as mock_call:
            with self.assert_program_exit('bad wolf'):
                app.bootstrap(self.env_name)
        mock_call.assert_called_once_with(
            self.juju, 'bootstrap', '-e', self.env_name),

    def test_status_retry_error(self, mock_print):
        # Before raising a ProgramExit, the functions tries to call
        # "juju status" multiple times if it exits with an error.
        side_effects = [
            (0, '', ''),  # Add the bootstrap call.
            # Add four status calls with a non-zero exit code.
            (1, '', 'these'),
            (2, '', 'are'),
            (3, '', 'the'),
            (4, '', 'voyages'),
            # Add a final valid status call.
            (0, self.make_status_output('started'), ''),
        ]
        self.assert_status_retried(side_effects)

    def test_status_retry_invalid_output(self, mock_print):
        # Before raising a ProgramExit, the functions tries to call
        # "juju status" multiple times if its output is not well formed or if
        # the agent is not started.
        side_effects = [
            (0, '', ''),  # Add the bootstrap call.
            (0, '', ''),  # Add the first status call: no output.
            (0, ':', ''),  # Add the second status call: not YAML.
            (0, 'just-a-string', ''),  # Add the third status call: bad YAML.
            # Add the fourth status call: the agent is still pending.
            (0, self.make_status_output('pending'), ''),
            # Add a final valid status call.
            (0, self.make_status_output('started'), ''),
        ]
        self.assert_status_retried(side_effects)

    def test_status_retry_both(self, mock_print):
        # Before raising a ProgramExit, the functions tries to call
        # "juju status" multiple times in any case.
        side_effects = [
            (0, '', ''),  # Add the bootstrap call.
            (1, '', 'error'),  # Add the first status call: error.
            (2, '', 'another error'),  # Add the second status call: error.
            # Add the third status call: the agent is still pending.
            (0, self.make_status_output('pending'), ''),
            (0, 'just-a-string', ''),  # Add the fourth status call: bad YAML.
            # Add a final valid status call.
            (0, self.make_status_output('started'), ''),
        ]
        self.assert_status_retried(side_effects)

    def test_agent_error(self, mock_print):
        # A ProgramExit is raised immediately if the Juju agent in the
        # bootstrap node is in an error state.
        status_output = self.make_status_output('error')
        side_effects = [
            (0, '', ''),  # Add the bootstrap call.
            (0, status_output, ''),  # Add the status call: agent error.
        ]
        expected = 'state server failure:\n{}'.format(status_output)
        with self.patch_multiple_calls(side_effects) as mock_call:
            with self.assert_program_exit(expected):
                app.bootstrap(self.env_name)
        mock_call.assert_has_calls([
            mock.call(self.juju, 'bootstrap', '-e', self.env_name),
        ] + self.make_status_calls(1))

    def test_status_failure(self, mock_print):
        # A ProgramExit is raised if "juju status" keeps failing.
        call_side_effects = [
            (0, '', ''),  # Add the bootstrap call.
            (1, 'output1', 'error1'),  # Add the first status call: retried.
            (1, 'output2', 'error2'),  # Add the second status call: error.
        ]
        time_side_effects = [
            0,  # Start at time zero (expiration at time 600).
            10,  # First call before the timeout expiration.
            100,  # Second call before the timeout expiration.
            1000,  # Third call after the timeout expiration.
        ]
        mock_time = mock.Mock(side_effect=time_side_effects)
        expected = 'the state server is not ready:\noutput2error2'
        with self.patch_multiple_calls(call_side_effects) as mock_call:
            # Simulate the timeout expired: the first time call is used to
            # calculate the timeout, the second one for the first status check,
            # the third for the second status check, the fourth should fail.
            with mock.patch('time.time', mock_time):
                with self.assert_program_exit(expected):
                    app.bootstrap(self.env_name)
        mock_call.assert_has_calls([
            mock.call(self.juju, 'bootstrap', '-e', self.env_name),
        ] + self.make_status_calls(2))


class TestGetAdminSecret(unittest.TestCase):

    def test_no_admin_secret(self):
        with mock.patch('quickstart.manage.envs.load_generated',
                        lambda x: {}):
            with self.assertRaises(ValueError) as exc:
                app.get_admin_secret('local', '/home/bac/.juju')
        expected = (
            u'admin-secret not found in '
            '/home/bac/.juju/environments/local.jenv')
        self.assertIn(expected, bytes(exc.exception))

    def test_success(self):
        expected = 'superchunk'
        with mock.patch('quickstart.manage.envs.load_generated',
                        lambda x: {'admin-secret': expected}):
            secret = app.get_admin_secret('local', '~bac/.juju')
        self.assertEqual(expected, secret)


class TestGetApiUrl(
        helpers.CallTestsMixin, ProgramExitTestsMixin, unittest.TestCase):

    env_name = 'ec2'

    def test_success(self):
        # The API URL is correctly returned.
        api_addresses = json.dumps(['api.example.com:17070', 'not-today'])
        with self.patch_call(retcode=0, output=api_addresses) as mock_call:
            api_url = app.get_api_url(self.env_name)
        self.assertEqual('wss://api.example.com:17070', api_url)
        mock_call.assert_called_once_with(
            '/usr/bin/juju', 'api-endpoints', '-e', self.env_name,
            '--format', 'json')

    def test_failure(self):
        # A ProgramExit is raised if an error occurs retrieving the API URL.
        with self.patch_call(retcode=1, error='bad wolf') as mock_call:
            with self.assert_program_exit('bad wolf'):
                app.get_api_url(self.env_name)
        mock_call.assert_called_once_with(
            '/usr/bin/juju', 'api-endpoints', '-e', self.env_name,
            '--format', 'json')


class TestConnect(ProgramExitTestsMixin, unittest.TestCase):

    admin_secret = 'Secret!'
    api_url = 'wss://api.example.com:17070'

    def test_connection_established(self):
        # The connection is done and the Environment instance is returned.
        with mock.patch('quickstart.juju.connect') as mock_connect:
            env = app.connect(self.api_url, self.admin_secret)
        mock_connect.assert_called_once_with(self.api_url)
        mock_env = mock_connect()
        mock_env.login.assert_called_once_with(self.admin_secret)
        self.assertEqual(mock_env, env)

    @mock.patch('time.sleep')
    @mock.patch('logging.warn')
    def test_connection_error(self, mock_warn, mock_sleep):
        # if an error occurs in the connection, it retries and then raises.
        mock_connect = mock.Mock(side_effect=ValueError('bad wolf'))
        expected = 'unable to connect to the Juju API server on {}: bad wolf'
        with mock.patch('quickstart.juju.connect', mock_connect):
            with self.assert_program_exit(expected.format(self.api_url)):
                app.connect(self.api_url, self.admin_secret)
        mock_connect.assert_called_with(self.api_url)
        self.assertEqual(30, mock_connect.call_count)
        mock_sleep.assert_called_with(1)
        self.assertEqual(29, mock_sleep.call_count)
        self.assertEqual(29, mock_warn.call_count)
        mock_warn.assert_called_with(
            'Retrying: ' + expected.format(self.api_url))

    @mock.patch('time.sleep')
    @mock.patch('logging.warn')
    def test_connection_retry(self, mock_warn, mock_sleep):
        # if an error occurs in the connection, it can succeed after retrying.
        mock_env = mock.Mock()
        mock_connect = mock.Mock(
            side_effect=[ValueError('bad wolf'), mock_env])
        with mock.patch('quickstart.juju.connect', mock_connect):
            env = app.connect(self.api_url, self.admin_secret)
        mock_connect.assert_called_with(self.api_url)
        self.assertEqual(2, mock_connect.call_count)
        mock_env.login.assert_called_once_with(self.admin_secret)
        self.assertEqual(mock_env, env)
        mock_sleep.assert_called_once_with(1)
        expected = 'unable to connect to the Juju API server on {}: bad wolf'
        mock_warn.assert_called_once_with(
            'Retrying: ' + expected.format(self.api_url))

    def test_authentication_error(self):
        # A ProgramExit is raised if an error occurs in the authentication.
        expected = 'unable to log in to the Juju API server on {}: bad wolf'
        with mock.patch('quickstart.juju.connect') as mock_connect:
            mock_login = mock_connect().login
            mock_login.side_effect = self.make_env_error('bad wolf')
            with self.assert_program_exit(expected.format(self.api_url)):
                app.connect(self.api_url, self.admin_secret)
        mock_connect.assert_called_with(self.api_url)
        mock_login.assert_called_once_with(self.admin_secret)

    def test_other_errors(self):
        # Any other errors occurred during the log in process are not trapped.
        error = ValueError('explode!')
        with mock.patch('quickstart.juju.connect') as mock_connect:
            mock_login = mock_connect().login
            mock_login.side_effect = error
            with self.assertRaises(ValueError) as context_manager:
                app.connect(self.api_url, self.admin_secret)
        self.assertIs(error, context_manager.exception)


class TestCreateAuthToken(unittest.TestCase):

    def test_success(self):
        # A successful call returns a token.
        env = mock.Mock()
        token = 'TOKEN-STRING'
        env.create_auth_token.return_value = {
            'Token': token,
            'Created': '2013-11-21T12:34:46.778866Z',
            'Expires': '2013-11-21T12:36:46.778866Z'
        }
        self.assertEqual(token, app.create_auth_token(env))

    def test_legacy_failure(self):
        # A legacy charm call returns None.
        env = mock.Mock()
        error = jujuclient.EnvError(
            {'Error': 'unknown object type "GUIToken"'})
        env.create_auth_token.side_effect = error
        self.assertIsNone(app.create_auth_token(env))

    def test_other_errors(self):
        # Any other errors are not trapped.
        env = mock.Mock()
        error = jujuclient.EnvError({
            'Error': 'tokens can only be created by authenticated users.',
            'ErrorCode': 'unauthorized access'
        })
        env.create_auth_token.side_effect = error
        with self.assertRaises(jujuclient.EnvError) as context_manager:
            app.create_auth_token(env)
        self.assertIs(error, context_manager.exception)


@helpers.mock_print
class TestDeployGui(
        ProgramExitTestsMixin, helpers.WatcherDataTestsMixin,
        unittest.TestCase):

    charm_url = 'cs:precise/juju-gui-100'

    def make_env(self, unit_name=None, service_data=None, unit_data=None):
        """Create and return a mock environment object.

        Set up the object so that a call to add_unit returns the given
        unit_name, and a call to status returns a status object containing the
        service and unit described by the given service_data and unit_data.
        """
        env = mock.Mock()
        # Set up the add_unit return value.
        if unit_name is not None:
            env.add_unit.return_value = {'Units': [unit_name]}
        #Set up the get_status return value.
        status = []
        if service_data is not None:
            status.append(self.make_service_change(data=service_data))
        if unit_data is not None:
            status.append(self.make_unit_change(data=unit_data))
        env.get_status.return_value = status
        return env

    def patch_get_charm_url(self, side_effect=None):
        """Patch the get_charm_url helper function."""
        if side_effect is None:
            side_effect = [self.charm_url]
        mock_get_charm_url = mock.Mock(side_effect=side_effect)
        return mock.patch('quickstart.utils.get_charm_url', mock_get_charm_url)

    def check_provided_charm_url(
            self, charm_url, mock_print, expected_logs=None):
        """Ensure the service is deployed and exposed with the given charm URL.

        Also check the expected warnings, if they are provided, are logged.
        """
        env = self.make_env(unit_name='my-gui/42')
        with helpers.assert_logs(expected_logs or [], level='warn'):
            app.deploy_gui(env, 'my-gui', '0', charm_url=charm_url)
        env.assert_has_calls([
            mock.call.deploy('my-gui', charm_url, num_units=0),
            mock.call.expose('my-gui'),
            mock.call.add_unit('my-gui', machine_spec='0'),
        ])
        mock_print.assert_has_calls([
            mock.call('requesting my-gui deployment'),
            mock.call('charm URL: {}'.format(charm_url)),
        ])

    def check_existing_charm_url(
            self, charm_url, mock_print, expected_logs=None):
        """Ensure the service is correctly found with the given charm URL.

        Also check the expected warnings, if they are provided, are logged.
        """
        service_data = {'CharmURL': charm_url}
        env = self.make_env(unit_name='my-gui/42', service_data=service_data)
        with helpers.assert_logs(expected_logs or [], level='warn'):
            app.deploy_gui(env, 'my-gui', '0', check_preexisting=True)
        env.assert_has_calls([
            mock.call.get_status(),
            mock.call.add_unit('my-gui', machine_spec='0'),
        ])
        mock_print.assert_has_calls([
            mock.call('service my-gui already deployed'),
            mock.call('charm URL: {}'.format(charm_url)),
        ])

    def test_deployment(self, mock_print):
        # The function correctly deploys and exposes the service, retrieving
        # the charm URL from the charmworld API.
        env = self.make_env(unit_name='my-gui/42')
        with self.patch_get_charm_url():
            unit_name = app.deploy_gui(env, 'my-gui', '0')
        self.assertEqual('my-gui/42', unit_name)
        env.assert_has_calls([
            mock.call.deploy('my-gui', self.charm_url, num_units=0),
            mock.call.expose('my-gui'),
            mock.call.add_unit('my-gui', machine_spec='0'),
        ])
        # There is no need to call status if the environment was just created.
        self.assertFalse(env.get_status.called)
        mock_print.assert_has_calls([
            mock.call('requesting my-gui deployment'),
            mock.call('charm URL: {}'.format(self.charm_url)),
            mock.call('my-gui deployment request accepted'),
            mock.call('exposing service my-gui'),
            mock.call('requesting new unit deployment'),
            mock.call('my-gui/42 deployment request accepted'),
        ])

    def test_existing_environment_without_entities(self, mock_print):
        # The deployment is processed in an already bootstrapped environment
        # with no relevant entities in it.
        env = self.make_env(unit_name='my-gui/42')
        with self.patch_get_charm_url():
            unit_name = app.deploy_gui(
                env, 'my-gui', '0', check_preexisting=True)
        self.assertEqual('my-gui/42', unit_name)
        env.assert_has_calls([
            mock.call.get_status(),
            mock.call.deploy('my-gui', self.charm_url, num_units=0),
            mock.call.expose('my-gui'),
            mock.call.add_unit('my-gui', machine_spec='0'),
        ])

    def test_default_charm_url(self, mock_print):
        # The function correctly deploys and exposes the service, even if it is
        # not able to retrieve the charm URL from the charmworld API.
        env = self.make_env(unit_name='my-gui/42')
        log = 'unable to retrieve the my-gui charm URL from the API: boo!'
        with self.patch_get_charm_url(side_effect=IOError('boo!')):
            # A warning is logged which notifies we are using the default URL.
            with helpers.assert_logs([log], level='warn'):
                app.deploy_gui(env, 'my-gui', '0')
        env.assert_has_calls([
            mock.call.deploy(
                'my-gui', settings.DEFAULT_CHARM_URL, num_units=0),
            mock.call.expose('my-gui'),
            mock.call.add_unit('my-gui', machine_spec='0'),
        ])
        mock_print.assert_has_calls([
            mock.call('requesting my-gui deployment'),
            mock.call('charm URL: {}'.format(settings.DEFAULT_CHARM_URL)),
        ])

    def test_existing_service(self, mock_print):
        # The deployment is executed reusing an already deployed service.
        env = self.make_env(unit_name='my-gui/42', service_data={})
        unit_name = app.deploy_gui(
            env, 'my-gui', '0', check_preexisting=True)
        self.assertEqual('my-gui/42', unit_name)
        env.assert_has_calls([
            mock.call.get_status(),
            mock.call.add_unit('my-gui', machine_spec='0'),
        ])
        # The service is not re-deployed.
        self.assertFalse(env.deploy.called)
        # The service is not re-exposed.
        self.assertFalse(env.expose.called)
        mock_print.assert_has_calls([
            mock.call('service my-gui already deployed'),
            mock.call('charm URL: cs:precise/juju-gui-47'),
            mock.call('requesting new unit deployment'),
            mock.call('my-gui/42 deployment request accepted'),
        ])

    def test_existing_service_unexposed(self, mock_print):
        # The existing service is exposed if required.
        service_data = {'Exposed': False}
        env = self.make_env(unit_name='my-gui/42', service_data=service_data)
        unit_name = app.deploy_gui(
            env, 'my-gui', '1', check_preexisting=True)
        self.assertEqual('my-gui/42', unit_name)
        env.assert_has_calls([
            mock.call.get_status(),
            mock.call.expose('my-gui'),
            mock.call.add_unit('my-gui', machine_spec='1'),
        ])
        # The service is not re-deployed.
        self.assertFalse(env.deploy.called)
        mock_print.assert_has_calls([
            mock.call('service my-gui already deployed'),
            mock.call('charm URL: cs:precise/juju-gui-47'),
            mock.call('exposing service my-gui'),
            mock.call('requesting new unit deployment'),
            mock.call('my-gui/42 deployment request accepted'),
        ])

    def test_existing_service_and_unit(self, mock_print):
        # A unit is reused if a suitable one is already present.
        env = self.make_env(service_data={}, unit_data={})
        unit_name = app.deploy_gui(
            env, 'my-gui', '0', check_preexisting=True)
        self.assertEqual('my-gui/47', unit_name)
        env.get_status.assert_called_once_with()
        # The service is not re-deployed.
        self.assertFalse(env.deploy.called)
        # The service is not re-exposed.
        self.assertFalse(env.expose.called)
        # The unit is not re-added.
        self.assertFalse(env.add_unit.called)
        mock_print.assert_has_calls([
            mock.call('service my-gui already deployed'),
            mock.call('charm URL: cs:precise/juju-gui-47'),
            mock.call('reusing unit my-gui/47'),
        ])

    def test_new_machine(self, mock_print):
        # The unit is correctly deployed in a new machine.
        env = self.make_env(unit_name='my-gui/42')
        with self.patch_get_charm_url():
            unit_name = app.deploy_gui(env, 'my-gui', None)
        self.assertEqual('my-gui/42', unit_name)
        env.assert_has_calls([
            mock.call.deploy('my-gui', self.charm_url, num_units=0),
            mock.call.expose('my-gui'),
            mock.call.add_unit('my-gui', machine_spec=None),
        ])

    def test_offical_charm_url_provided(self, mock_print):
        # The function correctly deploys and exposes the service using a user
        # provided revision of the Juju GUI charm URL.
        self.check_provided_charm_url('cs:precise/juju-gui-4242', mock_print)

    def test_customized_charm_url_provided(self, mock_print):
        # A customized charm URL is correctly recognized and logged if provided
        # by the user.
        self.check_provided_charm_url(
            'cs:~juju-gui/precise/juju-gui-42', mock_print,
            expected_logs=['using a customized juju-gui charm'])

    def test_outdated_charm_url_provided(self, mock_print):
        # An outdated charm URL is correctly recognized and logged if provided
        # by the user.
        self.check_provided_charm_url(
            'cs:precise/juju-gui-1', mock_print,
            expected_logs=[
                'charm is outdated and may not support bundle deployments'])

    def test_unexpected_charm_url_provided(self, mock_print):
        # An unexpected charm URL is correctly recognized and logged if
        # provided by the user.
        self.check_provided_charm_url(
            'cs:precise/exterminate-the-gui-666', mock_print,
            expected_logs=[
                'unexpected URL for the juju-gui charm: '
                'the service may not work as expected'])

    def test_offical_charm_url_existing(self, mock_print):
        # An existing official charm URL is correctly found.
        self.check_existing_charm_url('cs:precise/juju-gui-4242', mock_print)

    def test_customized_charm_url_existing(self, mock_print):
        # An existing customized charm URL is correctly found and logged.
        self.check_existing_charm_url(
            'cs:~juju-gui/precise/juju-gui-42', mock_print,
            expected_logs=['using a customized juju-gui charm'])

    def test_outdated_charm_url_existing(self, mock_print):
        # An existing but outdated charm URL is correctly found and logged.
        self.check_existing_charm_url(
            'cs:precise/juju-gui-1', mock_print,
            expected_logs=[
                'charm is outdated and may not support bundle deployments'])

    def test_unexpected_charm_url_existing(self, mock_print):
        # An existing but unexpected charm URL is correctly found and logged.
        self.check_existing_charm_url(
            'cs:precise/exterminate-the-gui-666', mock_print,
            expected_logs=[
                'unexpected URL for the juju-gui charm: '
                'the service may not work as expected'])

    def test_status_error(self, mock_print):
        # A ProgramExit is raised if an error occurs in the status API call.
        env = self.make_env()
        env.get_status.side_effect = self.make_env_error('bad wolf')
        with self.assert_program_exit('bad API response: bad wolf'):
            app.deploy_gui(
                env, 'another-gui', '0', check_preexisting=True)
        env.get_status.assert_called_once_with()

    def test_deploy_error(self, mock_print):
        # A ProgramExit is raised if an error occurs in the deploy API call.
        env = self.make_env()
        env.deploy.side_effect = self.make_env_error('bad wolf')
        with self.patch_get_charm_url():
            with self.assert_program_exit('bad API response: bad wolf'):
                app.deploy_gui(env, 'another-gui', '0')
        env.deploy.assert_called_once_with(
            'another-gui', self.charm_url, num_units=0)

    def test_expose_error(self, mock_print):
        # A ProgramExit is raised if an error occurs in the expose API call.
        env = self.make_env()
        env.expose.side_effect = self.make_env_error('bad wolf')
        with self.patch_get_charm_url():
            with self.assert_program_exit('bad API response: bad wolf'):
                app.deploy_gui(env, 'another-gui', '0')
        env.expose.assert_called_once_with('another-gui')

    def test_add_unit_error(self, mock_print):
        # A ProgramExit is raised if an error occurs in the add_unit API call.
        env = self.make_env()
        env.add_unit.side_effect = self.make_env_error('bad wolf')
        with self.patch_get_charm_url():
            with self.assert_program_exit('bad API response: bad wolf'):
                app.deploy_gui(env, 'another-gui', '0')
        env.add_unit.assert_called_once_with('another-gui', machine_spec='0')

    def test_other_errors(self, mock_print):
        # Any other errors occurred during the process are not trapped.
        error = ValueError('explode!')
        env = self.make_env(unit_name='my-gui/42')
        env.expose.side_effect = error
        with self.patch_get_charm_url():
            with self.assertRaises(ValueError) as context_manager:
                app.deploy_gui(env, 'juju-gui', '0')
        env.deploy.assert_called_once_with(
            'juju-gui', self.charm_url, num_units=0)
        env.expose.assert_called_once_with('juju-gui')
        self.assertIs(error, context_manager.exception)


@helpers.mock_print
class TestWatch(
        ProgramExitTestsMixin, helpers.ValueErrorTestsMixin,
        unittest.TestCase):

    address = 'unit.example.com'
    change_machine_pending = ('change', {
        'Id': '0',
        'Status': 'pending',
    })
    change_machine_started = ('change', {
        'Id': '0',
        'Status': 'started',
    })
    change_unit_pending = ('change', {
        'MachineId': '0',
        'Name': 'django/42',
        'PublicAddress': '',
        'Status': 'pending',
    })
    change_unit_reachable = ('change', {
        'MachineId': '0',
        'Name': 'django/42',
        'PublicAddress': address,
        'Status': 'pending',
    })
    change_unit_installed = ('change', {
        'MachineId': '0',
        'Name': 'django/42',
        'PublicAddress': address,
        'Status': 'installed',
    })
    change_unit_started = ('change', {
        'MachineId': '0',
        'Name': 'django/42',
        'PublicAddress': address,
        'Status': 'started',
    })
    machine_pending_call = mock.call('machine 0 provisioning is pending')
    machine_started_call = mock.call('machine 0 is started')
    unit_pending_call = mock.call('django/42 deployment is pending')
    unit_reachable_call = mock.call(
        'setting up django/42 on {}'.format(address))
    unit_installed_call = mock.call('django/42 is installed')
    unit_started_call = mock.call('django/42 is ready on machine 0')

    def make_env(self, changes):
        """Create and return a patched Environment instance.

        The watch_changes method of the resulting Environment object returns
        the provided changes.
        """
        env = mock.Mock()
        env.watch_changes().next.side_effect = changes
        return env

    # The following group of tests exercises both the function return value and
    # the function output, even if the output is handled by sub-functions.
    # This is done to simulate the different user experiences of observing the
    # environment evolution while the unit is deploying.

    def test_unit_life(self, mock_print):
        # The glorious moments in the unit's life are properly highlighted.
        # The machine achievements are also celebrated.
        env = self.make_env([
            ([self.change_unit_pending], [self.change_machine_pending]),
            ([], [self.change_machine_started]),
            ([self.change_unit_reachable], []),
            ([self.change_unit_installed], []),
            ([self.change_unit_started], []),
        ])
        address = app.watch(env, 'django/42')
        self.assertEqual(self.address, address)
        self.assertEqual(6, mock_print.call_count)
        mock_print.assert_has_calls([
            self.unit_pending_call,
            self.machine_pending_call,
            self.machine_started_call,
            self.unit_reachable_call,
            self.unit_installed_call,
            self.unit_started_call,
        ])

    def test_weird_order(self, mock_print):
        # Strange unit evolutions are handled.
        env = self.make_env([
            # The unit is first reachable and then pending. The machine starts
            # when the unit is already installed. All of this makes no sense
            # and should never happen, but if it does, we deal with it.
            ([self.change_unit_reachable], []),
            ([self.change_unit_pending], [self.change_machine_pending]),
            ([self.change_unit_installed], []),
            ([], [self.change_machine_started]),
            ([self.change_unit_started], []),
        ])
        address = app.watch(env, 'django/42')
        self.assertEqual(self.address, address)
        self.assertEqual(6, mock_print.call_count)
        mock_print.assert_has_calls([
            self.unit_reachable_call,
            self.unit_pending_call,
            self.machine_pending_call,
            self.unit_installed_call,
            self.machine_started_call,
            self.unit_started_call,
        ])

    def test_missing_changes(self, mock_print):
        # Only the unit started change is strictly required.
        env = self.make_env([([self.change_unit_started], [])])
        address = app.watch(env, 'django/42')
        self.assertEqual(self.address, address)
        self.assertEqual(2, mock_print.call_count)
        mock_print.assert_has_calls([
            self.unit_reachable_call,
            self.unit_started_call,
        ])

    def test_ignored_machine_changes(self, mock_print):
        # All machine changes are ignored until the application knows what
        # machine the unit belongs to.
        env = self.make_env([
            ([], [self.change_machine_pending]),
            ([], [self.change_machine_started]),
            ([self.change_unit_started], []),
        ])
        address = app.watch(env, 'django/42')
        self.assertEqual(self.address, address)
        # No machine related messages have been printed.
        self.assertEqual(2, mock_print.call_count)
        mock_print.assert_has_calls([
            self.unit_reachable_call,
            self.unit_started_call,
        ])

    def test_unit_already_deployed(self, mock_print):
        # Simulate the unit we are observing has been already deployed.
        # This happens, e.g., when executing Quickstart a second time, and both
        # the unit and the machine are already started.
        env = self.make_env([
            ([self.change_unit_started], [self.change_machine_started]),
        ])
        address = app.watch(env, 'django/42')
        self.assertEqual(self.address, address)
        self.assertEqual(2, mock_print.call_count)

    def test_machine_already_started(self, mock_print):
        # Simulate the unit is being deployed on an already started machine.
        # This happens, e.g., when running Quickstart on a non-local
        # environment type: the unit is deployed on the bootstrap node, which
        # is assumed to be started.
        env = self.make_env([
            ([self.change_unit_pending], [self.change_machine_started]),
            ([self.change_unit_reachable], []),
            ([self.change_unit_installed], []),
            ([self.change_unit_started], []),
        ])
        address = app.watch(env, 'django/42')
        self.assertEqual(self.address, address)
        self.assertEqual(5, mock_print.call_count)
        mock_print.assert_has_calls([
            self.unit_pending_call,
            self.machine_started_call,
            self.unit_reachable_call,
            self.unit_installed_call,
            self.unit_started_call,
        ])

    def test_extraneous_changes(self, mock_print):
        # Changes to units or machines we are not observing are ignored. Also
        # ensure that repeated changes to a single entity are ignored, even if
        # they are unlikely to happen.
        change_another_machine_pending = ('change', {
            'Id': '42',
            'Status': 'pending',
        })
        change_another_machine_started = ('change', {
            'Id': '1',
            'Status': 'started',
        })
        change_another_unit_pending = ('change', {
            'MachineId': '0',
            'Name': 'haproxy/0',
            'Status': 'pending',
        })
        change_another_unit_started = ('change', {
            'MachineId': '0',
            'Name': 'haproxy/0',
            'Status': 'started',
        })
        env = self.make_env([
            # Add a repeated change.
            ([self.change_unit_pending, self.change_unit_pending],
             [self.change_machine_pending]),
            # Add extraneous unit and machine changes.
            ([change_another_unit_pending], [change_another_machine_pending]),
            # Add a change to an extraneous machine.
            ([], [change_another_machine_started,
                  self.change_machine_started]),
            # Add a change to an extraneous unit.
            ([change_another_unit_started, self.change_unit_reachable], []),
            ([self.change_unit_installed], []),
            # Add another repeated change.
            ([self.change_unit_started, self.change_unit_started], []),
        ])
        address = app.watch(env, 'django/42')
        self.assertEqual(self.address, address)
        self.assertEqual(6, mock_print.call_count)
        mock_print.assert_has_calls([
            self.unit_pending_call,
            self.machine_pending_call,
            self.machine_started_call,
            self.unit_reachable_call,
            self.unit_installed_call,
            self.unit_started_call,
        ])

    def test_api_error(self, mock_print):
        # A ProgramExit is raised if an error occurs in one of the API calls.
        env = self.make_env([
            ([self.change_unit_pending], []),
            self.make_env_error('next returned an error'),
        ])
        expected = 'bad API server response: next returned an error'
        with self.assert_program_exit(expected):
            app.watch(env, 'django/42')
        self.assertEqual(1, mock_print.call_count)
        mock_print.assert_has_calls([self.unit_pending_call])

    def test_other_errors(self, mock_print):
        # Any other errors occurred during the process are not trapped.
        error = ValueError('explode!')
        env = self.make_env([([self.change_unit_installed], []), error])
        with self.assert_value_error('explode!'):
            app.watch(env, 'django/42')
        self.assertEqual(2, mock_print.call_count)
        mock_print.assert_has_calls([
            self.unit_reachable_call, self.unit_installed_call])

    def test_machine_status_error(self, mock_print):
        # A ProgramExit is raised if an the machine is found in an error state.
        change_machine_error = ('change', {
            'Id': '0',
            'Status': 'error',
            'StatusInfo': 'oddities',
        })
        # The unit pending change is required to make the function know which
        # machine to observe.
        env = self.make_env([(
            [self.change_unit_pending], [change_machine_error]),
        ])
        expected = 'machine 0 is in an error state: error: oddities'
        with self.assert_program_exit(expected):
            app.watch(env, 'django/42')
        self.assertEqual(1, mock_print.call_count)
        mock_print.assert_has_calls([self.unit_pending_call])

    def test_unit_status_error(self, mock_print):
        # A ProgramExit is raised if an the unit is found in an error state.
        change_unit_error = ('change', {
            'MachineId': '0',
            'Name': 'django/42',
            'Status': 'error',
            'StatusInfo': 'install failure',
        })
        env = self.make_env([([change_unit_error], [])])
        expected = 'django/42 is in an error state: error: install failure'
        with self.assert_program_exit(expected):
            app.watch(env, 'django/42')
        self.assertFalse(mock_print.called)


class TestDeployBundle(ProgramExitTestsMixin, unittest.TestCase):

    name = 'mybundle'
    yaml = 'mybundle: contents'
    bundle_id = '~fake/basket/bundle'

    def test_bundle_deployment(self):
        # A bundle is successfully deployed.
        env = mock.Mock()
        app.deploy_bundle(env, self.yaml, self.name, self.bundle_id)
        env.deploy_bundle.assert_called_once_with(
            self.yaml, name=self.name, bundle_id=self.bundle_id)
        self.assertFalse(env.close.called)

    def test_api_error(self):
        # A ProgramExit is raised if an error occurs in one of the API calls.
        env = mock.Mock()
        env.deploy_bundle.side_effect = self.make_env_error(
            'bundle deployment failure')
        expected = 'bad API server response: bundle deployment failure'
        with self.assert_program_exit(expected):
            app.deploy_bundle(env, self.yaml, self.name, self.bundle_id)

    def test_other_errors(self):
        # Any other errors occurred during the process are not trapped.
        env = mock.Mock()
        error = ValueError('explode!')
        env.deploy_bundle.side_effect = error
        with self.assertRaises(ValueError) as context_manager:
            app.deploy_bundle(env, self.yaml, self.name, None)
        self.assertIs(error, context_manager.exception)
