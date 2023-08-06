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

"""Tests for the Juju Quickstart management infrastructure."""

from __future__ import unicode_literals

import argparse
from contextlib import contextmanager
import logging
import os
import shutil
import StringIO as io
import tempfile
import unittest

import mock
import yaml

import quickstart
from quickstart import (
    manage,
    settings,
)
from quickstart.cli import views
from quickstart.models import envs
from quickstart.tests import helpers
from quickstart import app


class TestDescriptionAction(unittest.TestCase):

    def setUp(self):
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument(
            '--test', action=manage._DescriptionAction, nargs=0)

    @mock.patch('sys.exit')
    @helpers.mock_print
    def test_action(self, mock_print, mock_exit):
        # The action just prints the description and exits.
        args = self.parser.parse_args(['--test'])
        self.assertIsNone(args.test)
        mock_print.assert_called_once_with(settings.DESCRIPTION)
        mock_exit.assert_called_once_with(0)


class TestValidateBundle(
        helpers.BundleFileTestsMixin, helpers.UrlReadTestsMixin,
        unittest.TestCase):

    def setUp(self):
        self.parser = mock.Mock()

    def make_options(self, bundle, bundle_name=None):
        """Return a mock options object which includes the passed arguments."""
        return mock.Mock(bundle=bundle, bundle_name=bundle_name)

    def test_resulting_options_from_file(self):
        # The options object is correctly set up when a bundle file is passed.
        bundle_file = self.make_bundle_file()
        options = self.make_options(bundle_file, bundle_name='bundle1')
        manage._validate_bundle(options, self.parser)
        self.assertEqual('bundle1', options.bundle_name)
        self.assertEqual(
            ['mysql', 'wordpress'], sorted(options.bundle_services))
        self.assertEqual(open(bundle_file).read(), options.bundle_yaml)

    def test_resulting_options_from_url(self):
        # The options object is correctly set up when a bundle HTTP(S) URL is
        # passed.
        bundle_file = self.make_bundle_file()
        url = 'http://example.com/bundle.yaml'
        options = self.make_options(url, bundle_name='bundle1')
        with self.patch_urlread(contents=self.valid_bundle) as mock_urlread:
            manage._validate_bundle(options, self.parser)
        mock_urlread.assert_called_once_with(url)
        self.assertEqual('bundle1', options.bundle_name)
        self.assertEqual(
            ['mysql', 'wordpress'], sorted(options.bundle_services))
        self.assertEqual(open(bundle_file).read(), options.bundle_yaml)

    def test_resulting_options_from_bundle_url(self):
        # The options object is correctly set up when a "bundle:" URL is
        # passed.
        bundle_file = self.make_bundle_file()
        url = 'bundle:~who/my/bundle'
        options = self.make_options(url, bundle_name='bundle1')
        with self.patch_urlread(contents=self.valid_bundle) as mock_urlread:
            manage._validate_bundle(options, self.parser)
        mock_urlread.assert_called_once_with(
            'https://manage.jujucharms.com/bundle/~who/my/bundle/json')
        self.assertEqual('bundle1', options.bundle_name)
        self.assertEqual(
            ['mysql', 'wordpress'], sorted(options.bundle_services))
        self.assertEqual(open(bundle_file).read(), options.bundle_yaml)

    def test_resulting_options_from_dir(self):
        # The options object is correctly set up when a bundle dir is passed.
        bundle_dir = self.make_bundle_dir()
        options = self.make_options(bundle_dir, bundle_name='bundle1')
        manage._validate_bundle(options, self.parser)
        self.assertEqual('bundle1', options.bundle_name)
        self.assertEqual(
            ['mysql', 'wordpress'], sorted(options.bundle_services))
        expected = open(os.path.join(bundle_dir, 'bundles.yaml')).read()
        self.assertEqual(expected, options.bundle_yaml)

    def test_expand_user(self):
        # The ~ construct is correctly expanded in the validation process.
        bundle_file = self.make_bundle_file()
        # Split the full path of the bundle file, e.g. from a full
        # "/tmp/bundle.file" path retrieve the base path "/tmp" and the file
        # name "bundle.file". By doing that we can simulate that the user's
        # home is "/tmp" and that the bundle file is "~/bundle.file".
        base_path, filename = os.path.split(bundle_file)
        path = '~/{}'.format(filename)
        options = self.make_options(bundle=path, bundle_name='bundle2')
        with mock.patch('os.environ', {'HOME': base_path}):
            manage._validate_bundle(options, self.parser)
        self.assertEqual(self.valid_bundle, options.bundle_yaml)

    def test_bundle_file_not_found(self):
        # A parser error is invoked if the bundle file is not found.
        options = self.make_options('/no/such/file.yaml')
        manage._validate_bundle(options, self.parser)
        expected = (
            'unable to open bundle file: '
            "[Errno 2] No such file or directory: '/no/such/file.yaml'"
        )
        self.parser.error.assert_called_once_with(expected)

    def test_bundle_dir_not_valid(self):
        # A parser error is invoked if the bundle dir does not contain the
        # bundles.yaml file.
        bundle_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, bundle_dir)
        options = self.make_options(bundle_dir)
        manage._validate_bundle(options, self.parser)
        expected = (
            'unable to open bundle file: '
            "[Errno 2] No such file or directory: '{}/bundles.yaml'"
        ).format(bundle_dir)
        self.parser.error.assert_called_once_with(expected)

    def test_url_error(self):
        # A parser error is invoked if the bundle cannot be fetched from the
        # provided URL.
        url = 'http://example.com/bundle.yaml'
        options = self.make_options(url)
        with self.patch_urlread(error=True) as mock_urlread:
            manage._validate_bundle(options, self.parser)
        mock_urlread.assert_called_once_with(url)
        self.parser.error.assert_called_once_with(
            'unable to open bundle URL: bad wolf')

    def test_bundle_url_error(self):
        # A parser error is invoked if an invalid "bundle:" URL is provided.
        url = 'bundle:'
        options = self.make_options(url)
        manage._validate_bundle(options, self.parser)
        self.parser.error.assert_called_once_with(
            'unable to open the bundle: invalid bundle URL: bundle:')

    def test_error_parsing_bundle_contents(self):
        # A parser error is invoked if an error occurs parsing the bundle YAML.
        bundle_file = self.make_bundle_file()
        options = self.make_options(bundle_file, bundle_name='no-such')
        manage._validate_bundle(options, self.parser)
        expected = ('bundle no-such not found in the provided list of bundles '
                    '(bundle1, bundle2)')
        self.parser.error.assert_called_once_with(expected)


class TestValidateCharmUrl(unittest.TestCase):

    def setUp(self):
        self.parser = mock.Mock()

    def make_options(self, charm_url, has_bundle=False):
        """Return a mock options object which includes the passed arguments."""
        options = mock.Mock(charm_url=charm_url, bundle=None)
        if has_bundle:
            options.bundle = 'bundle:~who/django/42/django'
        return options

    def test_invalid_url_error(self):
        # A parser error is invoked if the charm URL is not valid.
        options = self.make_options('cs:invalid')
        manage._validate_charm_url(options, self.parser)
        expected = 'charm URL has invalid form: cs:invalid'
        self.parser.error.assert_called_once_with(expected)

    def test_local_charm_error(self):
        # A parser error is invoked if a local charm is provided.
        options = self.make_options('local:precise/juju-gui-100')
        manage._validate_charm_url(options, self.parser)
        expected = 'local charms are not allowed: local:precise/juju-gui-100'
        self.parser.error.assert_called_once_with(expected)

    def test_unsupported_series_error(self):
        # A parser error is invoked if the charm series is not supported.
        options = self.make_options('cs:nosuch/juju-gui-100')
        manage._validate_charm_url(options, self.parser)
        expected = 'unsupported charm series: nosuch'
        self.parser.error.assert_called_once_with(expected)

    def test_outdated_charm_error(self):
        # A parser error is invoked if a bundle deployment has been requested
        # but the provided charm does not support bundles.
        options = self.make_options('cs:precise/juju-gui-1', has_bundle=True)
        manage._validate_charm_url(options, self.parser)
        expected = (
            'bundle deployments not supported by the requested charm '
            'revision: cs:precise/juju-gui-1')
        self.parser.error.assert_called_once_with(expected)

    def test_outdated_allowed_without_bundles(self):
        # An outdated charm is allowed if no bundles are provided.
        options = self.make_options('cs:precise/juju-gui-1', has_bundle=False)
        manage._validate_charm_url(options, self.parser)
        self.assertFalse(self.parser.error.called)

    def test_success(self):
        # The functions completes without error if the charm URL is valid.
        good = (
            'cs:precise/juju-gui-100',
            'cs:~juju-gui/precise/juju-gui-42',
            'cs:~who/precise/juju-gui-42',
            'cs:~who/precise/my-juju-gui-42',
        )
        for charm_url in good:
            options = self.make_options(charm_url)
            manage._validate_charm_url(options, self.parser)
            self.assertFalse(self.parser.error.called, charm_url)


class TestRetrieveEnvDb(helpers.EnvFileTestsMixin, unittest.TestCase):

    def setUp(self):
        self.parser = mock.Mock()

    def test_existing_env_file(self):
        # The env_db is correctly retrieved from an existing environments file.
        env_file = self.make_env_file()
        env_db = manage._retrieve_env_db(self.parser, env_file=env_file)
        self.assertEqual(yaml.safe_load(self.valid_contents), env_db)

    def test_error_parsing_env_file(self):
        # A parser error is invoked if an error occurs parsing the env file.
        env_file = self.make_env_file('so-bad')
        manage._retrieve_env_db(self.parser, env_file=env_file)
        self.parser.error.assert_called_once_with(
            'invalid YAML contents in {}: so-bad'.format(env_file))

    def test_missing_env_file(self):
        # An empty env_db is returned if the environments file does not exist.
        env_db = manage._retrieve_env_db(self.parser, env_file=None)
        self.assertEqual(envs.create_empty_env_db(), env_db)


@mock.patch('quickstart.manage.envs.save')
class TestCreateSaveCallable(unittest.TestCase):

    def setUp(self):
        self.parser = mock.Mock()
        self.env_file = '/tmp/envfile.yaml'
        self.env_db = helpers.make_env_db()
        with mock.patch('quickstart.manage.utils.run_once') as mock_run_once:
            self.save_callable = manage._create_save_callable(
                self.parser, self.env_file)
        self.mock_run_once = mock_run_once

    def test_saved(self, mock_save):
        # The returned function correctly saves the new environments database.
        self.save_callable(self.env_db)
        mock_save.assert_called_once_with(
            self.env_file, self.env_db, backup_function=self.mock_run_once())
        self.assertFalse(self.parser.error.called)

    def test_error(self, mock_save):
        # The returned function uses the parser to exit the program if an error
        # occurs while saving the new environments database.
        mock_save.side_effect = OSError(b'bad wolf')
        self.save_callable(self.env_db)
        mock_save.assert_called_once_with(
            self.env_file, self.env_db, backup_function=self.mock_run_once())
        self.parser.error.assert_called_once_with('bad wolf')

    def test_backup_function(self, mock_save):
        # The backup function is correctly created.
        self.save_callable(self.env_db)
        self.mock_run_once.assert_called_once_with(shutil.copyfile)


class TestStartInteractiveSession(
        helpers.EnvFileTestsMixin, unittest.TestCase):

    def setUp(self):
        # Set up a parser, the environments metadata, an environments file and
        # a testing env_db.
        self.parser = mock.Mock()
        self.env_type_db = envs.get_env_type_db()
        self.env_file = self.make_env_file()
        self.env_db = envs.load(self.env_file)

    @contextmanager
    def patch_interactive_mode(self, env_db, return_value):
        """Patch the quickstart.cli.views.show function.

        Ensure the interactive mode is started by the code in the context block
        passing the given env_db. Make the view return the given return_value.
        """
        create_save_callable_path = 'quickstart.manage._create_save_callable'
        mock_show = mock.Mock(return_value=return_value)
        with mock.patch(create_save_callable_path) as mock_save_callable:
            with mock.patch('quickstart.manage.views.show', mock_show):
                yield
        mock_save_callable.assert_called_once_with(self.parser, self.env_file)
        mock_show.assert_called_once_with(
            views.env_index, self.env_type_db, env_db,
            mock_save_callable())

    def test_resulting_env_data(self):
        # The interactive session can be used to select an environment, in
        # which case the function returns the corresponding env_data.
        env_data = envs.get_env_data(self.env_db, 'aws')
        with self.patch_interactive_mode(self.env_db, [self.env_db, env_data]):
            obtained_env_data = manage._start_interactive_session(
                self.parser, self.env_type_db, self.env_db, self.env_file)
        self.assertEqual(env_data, obtained_env_data)

    @helpers.mock_print
    def test_modified_environments(self, mock_print):
        # The function informs the user that environments have been modified
        # during the interactive session.
        env_data = envs.get_env_data(self.env_db, 'aws')
        new_env_db = helpers.make_env_db()
        with self.patch_interactive_mode(self.env_db, [new_env_db, env_data]):
            manage._start_interactive_session(
                self.parser, self.env_type_db, self.env_db, self.env_file)
        mock_print.assert_called_once_with(
            'changes to the environments file have been saved')

    @mock.patch('sys.exit')
    def test_interactive_mode_quit(self, mock_exit):
        # If the user explicitly quits the interactive mode, the program exits
        # without proceeding with the environment bootstrapping.
        with self.patch_interactive_mode(self.env_db, [self.env_db, None]):
            manage._start_interactive_session(
                self.parser, self.env_type_db, self.env_db, self.env_file)
        mock_exit.assert_called_once_with('quitting')


class TestRetrieveEnvData(unittest.TestCase):

    def setUp(self):
        # Set up a parser, the environments metadata and a testing env_db.
        self.parser = mock.Mock()
        self.env_type_db = envs.get_env_type_db()
        self.env_db = helpers.make_env_db()

    def test_resulting_env_data(self):
        # The env_data is correctly validated and returned.
        expected_env_data = envs.get_env_data(self.env_db, 'lxc')
        env_data = manage._retrieve_env_data(
            self.parser, self.env_type_db, self.env_db, 'lxc')
        self.assertEqual(expected_env_data, env_data)

    def test_error_environment_not_found(self):
        # A parser error is invoked if the provided environment is not included
        # in the environments database.
        manage._retrieve_env_data(
            self.parser, self.env_type_db, self.env_db, 'no-such')
        self.parser.error.assert_called_once_with(
            'environment no-such not found')

    def test_error_environment_not_valid(self):
        # A parser error is invoked if the selected environment is not valid.
        manage._retrieve_env_data(
            self.parser, self.env_type_db, self.env_db, 'local-with-errors')
        self.parser.error.assert_called_once_with(
            'cannot use the local-with-errors environment:\n'
            'the storage port field requires an integer value')


class TestSetupEnv(helpers.EnvFileTestsMixin, unittest.TestCase):

    def setUp(self):
        self.parser = mock.Mock()

    def make_options(self, env_file, env_name=None, interactive=False):
        """Return a mock options object which includes the passed arguments."""
        return mock.Mock(
            env_file=env_file,
            env_name=env_name,
            interactive=interactive,
        )

    def patch_interactive_mode(self, return_value):
        """Patch the quickstart.manage._start_interactive_session function.

        Make the mocked function return the given return_value.
        """
        mock_start_interactive_session = mock.Mock(return_value=return_value)
        return mock.patch(
            'quickstart.manage._start_interactive_session',
            mock_start_interactive_session)

    def test_resulting_options(self):
        # The options object is correctly set up.
        env_file = self.make_env_file()
        options = self.make_options(
            env_file, env_name='aws', interactive=False)
        manage._setup_env(options, self.parser)
        self.assertEqual('Secret!', options.admin_secret)
        self.assertEqual(env_file, options.env_file)
        self.assertEqual('aws', options.env_name)
        self.assertEqual('ec2', options.env_type)
        self.assertEqual('saucy', options.default_series)
        self.assertFalse(options.interactive)

    def test_expand_user(self):
        # The ~ construct is correctly expanded in the validation process.
        env_file = self.make_env_file()
        # Split the full path of the env file, e.g. from a full "/tmp/env.file"
        # path retrieve the base path "/tmp" and the file name "env.file".
        # By doing that we can simulate that the user's home is "/tmp" and that
        # the env file is "~/env.file".
        base_path, filename = os.path.split(env_file)
        path = '~/{}'.format(filename)
        options = self.make_options(env_file=path, env_name='aws')
        with mock.patch('os.environ', {'HOME': base_path}):
            manage._setup_env(options, self.parser)
        self.assertEqual(env_file, options.env_file)

    def test_no_env_name(self):
        # A parser error is invoked if the environment name is missing and
        # interactive mode is disabled.
        options = self.make_options(self.make_env_file(), interactive=False)
        manage._setup_env(options, self.parser)
        self.assertTrue(self.parser.error.called)
        message = self.parser.error.call_args[0][0]
        self.assertIn('unable to find an environment name to use', message)

    def test_local_provider(self):
        # Local environments are correctly handled.
        contents = yaml.safe_dump({
            'environments': {
                'lxc': {'admin-secret': 'Secret!', 'type': 'local'},
            },
        })
        env_file = self.make_env_file(contents)
        options = self.make_options(
            env_file, env_name='lxc', interactive=False)
        manage._setup_env(options, self.parser)
        self.assertEqual('Secret!', options.admin_secret)
        self.assertEqual(env_file, options.env_file)
        self.assertEqual('lxc', options.env_name)
        self.assertEqual('local', options.env_type)
        self.assertIsNone(options.default_series)
        self.assertFalse(options.interactive)

    def test_interactive_mode(self):
        # The interactive mode is started properly if the corresponding option
        # flag is set.
        env_file = self.make_env_file()
        options = self.make_options(env_file, interactive=True)
        # Simulate the user did not make any changes to the env_db from the
        # interactive session.
        env_db = yaml.load(self.valid_contents)
        # Simulate the aws environment has been selected and started from the
        # interactive session.
        env_data = envs.get_env_data(env_db, 'aws')
        get_env_type_db_path = 'quickstart.models.envs.get_env_type_db'
        with mock.patch(get_env_type_db_path) as mock_get_env_type_db:
            with self.patch_interactive_mode(env_data) as mock_interactive:
                manage._setup_env(options, self.parser)
        mock_interactive.assert_called_once_with(
            self.parser, mock_get_env_type_db(), env_db, env_file)
        # The options is updated with data from the selected environment.
        self.assertEqual('Secret!', options.admin_secret)
        self.assertEqual(env_file, options.env_file)
        self.assertEqual('aws', options.env_name)
        self.assertEqual('ec2', options.env_type)
        self.assertEqual('saucy', options.default_series)
        self.assertTrue(options.interactive)

    @helpers.mock_print
    def test_missing_env_file(self, mock_print):
        # If the environments file does not exist, an empty env_db is created
        # in memory and interactive mode is forced.
        new_env_db = helpers.make_env_db()
        env_data = envs.get_env_data(new_env_db, 'lxc')
        options = self.make_options('__no_such_env_file__', interactive=False)
        # In this case, we expect the interactive mode to be started and the
        # env_db passed to the view to be an empty one.
        with self.patch_interactive_mode(env_data) as mock_interactive:
            manage._setup_env(options, self.parser)
        self.assertTrue(mock_interactive.called)
        self.assertTrue(options.interactive)


class TestConvertOptionsToUnicode(unittest.TestCase):

    def test_bytes_options(self):
        # Byte strings are correctly converted.
        options = argparse.Namespace(opt1=b'val1', opt2=b'val2')
        manage._convert_options_to_unicode(options)
        self.assertEqual('val1', options.opt1)
        self.assertIsInstance(options.opt1, unicode)
        self.assertEqual('val2', options.opt2)
        self.assertIsInstance(options.opt2, unicode)

    def test_unicode_options(self):
        # Unicode options are left untouched.
        options = argparse.Namespace(myopt='myval')
        self.assertEqual('myval', options.myopt)
        self.assertIsInstance(options.myopt, unicode)

    def test_other_types(self):
        # Other non-string types are left untouched.
        options = argparse.Namespace(opt1=42, opt2=None)
        self.assertEqual(42, options.opt1)
        self.assertIsNone(options.opt2)


@mock.patch('quickstart.manage._setup_env', mock.Mock())
class TestSetup(unittest.TestCase):

    def patch_get_default_env_name(self, env_name=None):
        """Patch the function used by setup() to retrieve the default env name.

        This way the test does not rely on the user's Juju environment set up,
        and it is also possible to simulate an arbitrary environment name.
        """
        mock_get_default_env_name = mock.Mock(return_value=env_name)
        path = 'quickstart.manage.envs.get_default_env_name'
        return mock.patch(path, mock_get_default_env_name)

    def call_setup(self, args, env_name='ec2', exit_called=True):
        """Call the setup function simulating the given args and env name.

        Also ensure the program exits without errors if exit_called is True.
        """
        with mock.patch('sys.argv', ['juju-quickstart'] + args):
            with mock.patch('sys.exit') as mock_exit:
                with self.patch_get_default_env_name(env_name):
                    manage.setup()
        if exit_called:
            mock_exit.assert_called_once_with(0)

    def test_help(self):
        # The program help message is properly formatted.
        with mock.patch('sys.stdout') as mock_stdout:
            self.call_setup(['--help'])
        stdout_write = mock_stdout.write
        self.assertTrue(stdout_write.called)
        # Retrieve the output from the mock call.
        output = stdout_write.call_args[0][0]
        self.assertIn('usage: juju-quickstart', output)
        # NB: some shells break the docstring at different places when --help
        # is called so the replacements below make it agnostic.
        self.assertIn(quickstart.__doc__.replace('\n', ' '),
                      output.replace('\n', ' '))
        self.assertIn('--environment', output)
        # Without a default environment, the -e option has no default.
        self.assertIn('The name of the Juju environment to use (ec2)\n',
                      output)

    def test_help_with_default_environment(self):
        # The program help message is properly formatted when a default Juju
        # environment is found.
        with mock.patch('sys.stdout') as mock_stdout:
            self.call_setup(['--help'], env_name='hp')
        stdout_write = mock_stdout.write
        self.assertTrue(stdout_write.called)
        # Retrieve the output from the mock call.
        output = stdout_write.call_args[0][0]
        self.assertIn('The name of the Juju environment to use (hp)\n', output)

    def test_description(self):
        # The program description is properly printed out as required by juju.
        with helpers.mock_print as mock_print:
            self.call_setup(['--description'])
        mock_print.assert_called_once_with(settings.DESCRIPTION)

    def test_version(self):
        # The program version is properly printed to stderr.
        with mock.patch('sys.stderr', new_callable=io.StringIO) as mock_stderr:
            self.call_setup(['--version'])
        expected = 'juju-quickstart {}\n'.format(quickstart.get_version())
        self.assertEqual(expected, mock_stderr.getvalue())

    @mock.patch('quickstart.manage._validate_bundle')
    def test_bundle(self, mock_validate_bundle):
        # The bundle validation process is started if a bundle is provided.
        self.call_setup(['/path/to/bundle.file'], exit_called=False)
        self.assertTrue(mock_validate_bundle.called)
        options, parser = mock_validate_bundle.call_args_list[0][0]
        self.assertIsInstance(options, argparse.Namespace)
        self.assertIsInstance(parser, argparse.ArgumentParser)

    @mock.patch('quickstart.manage._validate_charm_url')
    def test_charm_url(self, mock_validate_charm_url):
        # The charm URL validation process is started if a URL is provided.
        self.call_setup(
            ['--gui-charm-url', 'cs:precise/juju-gui-42'], exit_called=False)
        self.assertTrue(mock_validate_charm_url.called)
        options, parser = mock_validate_charm_url.call_args_list[0][0]
        self.assertIsInstance(options, argparse.Namespace)
        self.assertIsInstance(parser, argparse.ArgumentParser)

    def test_configure_logging(self):
        # Logging is properly set up at the info level.
        logger = logging.getLogger()
        self.call_setup([], 'ec2', exit_called=False)
        self.assertEqual(logging.INFO, logger.level)

    def test_configure_logging_debug(self):
        # Logging is properly set up at the debug level.
        logger = logging.getLogger()
        self.call_setup(['--debug'], 'ec2', exit_called=False)
        self.assertEqual(logging.DEBUG, logger.level)


@mock.patch('webbrowser.open')
@mock.patch('quickstart.manage.app')
@mock.patch('__builtin__.print', mock.Mock())
class TestRun(unittest.TestCase):

    def make_options(self, **kwargs):
        """Set up the options to be passed to the run function."""
        options = {
            'admin_secret': 'Secret!',
            'bundle': None,
            'bundle_id': None,
            'charm_url': None,
            'debug': False,
            'env_name': 'aws',
            'env_type': 'ec2',
            'open_browser': True,
            'default_series': None,
        }
        options.update(kwargs)
        return mock.Mock(**options)

    @staticmethod
    def mock_get_admin_secret_success(name, home):
        return 'jenv secret'

    @staticmethod
    def mock_get_admin_secret_error(name, home):
        fn = '{}.jenv'.format(name)
        path = os.path.join(home, 'environments', fn)
        msg = 'admin-secret not found in {}'.format(path)
        raise ValueError(msg.encode('utf-8'))

    def test_no_bundle(self, mock_app, mock_open):
        # The application runs correctly if no bundle is provided.
        token = 'AUTHTOKEN'
        mock_app.create_auth_token.return_value = token
        mock_app.watch.return_value = '1.2.3.4'
        mock_app.bootstrap.return_value = (True, 'precise')
        mock_app.get_admin_secret = self.mock_get_admin_secret_error
        options = self.make_options()
        manage.run(options)
        mock_app.ensure_dependencies.assert_called()
        mock_app.ensure_ssh_keys.assert_called()
        mock_app.bootstrap.assert_called_once_with(
            options.env_name, requires_sudo=mock_app.bootstrap_requires_sudo(),
            debug=options.debug)
        mock_app.get_api_url.assert_called_once_with(options.env_name)
        mock_app.connect.assert_has_calls([
            mock.call(mock_app.get_api_url(), options.admin_secret),
            mock.call().close(),
            mock.call('wss://1.2.3.4:443/ws', options.admin_secret),
            mock.call().close(),
        ])
        mock_app.deploy_gui.assert_called_once_with(
            mock_app.connect(), settings.JUJU_GUI_SERVICE_NAME, '0',
            charm_url=options.charm_url,
            check_preexisting=mock_app.bootstrap()[0])
        mock_app.watch.assert_called_once_with(
            mock_app.connect(), mock_app.deploy_gui())
        mock_app.create_auth_token.assert_called_once_with(mock_app.connect())
        mock_open.assert_called_once_with(
            'https://{}/?authtoken={}'.format(mock_app.watch(), token))
        self.assertFalse(mock_app.deploy_bundle.called)

    def test_no_token(self, mock_app, mock_open):
        mock_app.create_auth_token.return_value = None
        mock_app.bootstrap.return_value = (True, 'precise')
        options = self.make_options()
        manage.run(options)
        mock_app.create_auth_token.assert_called_once_with(mock_app.connect())
        mock_open.assert_called_once_with(
            'https://{}'.format(mock_app.watch()))

    def test_bundle(self, mock_app, mock_open):
        # A bundle is correctly deployed by the application.
        options = self.make_options(
            bundle='/my/bundle/file.yaml', bundle_yaml='mybundle: contents',
            bundle_name='mybundle', bundle_services=['service1', 'service2'])
        mock_app.bootstrap.return_value = (True, 'precise')
        mock_app.watch.return_value = 'gui.example.com'
        manage.run(options)
        mock_app.deploy_bundle.assert_called_once_with(
            mock_app.connect(), 'mybundle: contents', 'mybundle', None)

    def test_local_provider_no_sudo(self, mock_app, mock_open):
        # The application correctly handles working with local providers with
        # new Juju versions not requiring "sudo" to bootstrap the environment.
        options = self.make_options(env_type='local')
        mock_app.bootstrap_requires_sudo.return_value = False
        mock_app.bootstrap.return_value = (True, 'precise')
        manage.run(options)
        mock_app.bootstrap.assert_called_once_with(
            options.env_name, requires_sudo=False, debug=options.debug)

    def test_local_provider_req_sudo(self, mock_app, mock_open):
        # The application correctly handles working with local providers when
        # Juju requires an external "sudo" call to bootstrap the environment.
        options = self.make_options(env_type='local')
        mock_app.bootstrap_requires_sudo.return_value = True
        mock_app.bootstrap.return_value = (True, 'precise')
        manage.run(options)
        mock_app.bootstrap.assert_called_once_with(
            options.env_name, requires_sudo=True, debug=options.debug)

    def test_no_browser(self, mock_app, mock_open):
        # It is possible to avoid opening the GUI in the browser.
        mock_app.bootstrap.return_value = (True, 'precise')
        options = self.make_options(open_browser=False)
        manage.run(options)
        self.assertFalse(mock_open.called)

    def test_admin_secret_fetched(self, mock_app, mock_open):
        # If an admin secret is fetched from jenv it is used, even if one is
        # found in environments.yaml, as set in options.admin_secret.
        mock_app.get_admin_secret = self.mock_get_admin_secret_success
        mock_app.bootstrap.return_value = (True, 'precise')
        options = self.make_options(admin_secret='secret in environments.yaml')
        manage.run(options)
        mock_app.connect.assert_has_calls([
            mock.call(mock_app.get_api_url(), 'jenv secret'),
        ])

    def test_admin_secret_from_environments_yaml(self, mock_app, mock_open):
        # If an admin secret is not fetched from jenv, then the one from
        # environments.yaml is used, as found in options.admin_secret.
        mock_app.get_admin_secret = self.mock_get_admin_secret_error
        mock_app.bootstrap.return_value = (True, 'precise')
        options = self.make_options(admin_secret='secret in environments.yaml')
        manage.run(options)
        mock_app.connect.assert_has_calls([
            mock.call(mock_app.get_api_url(), 'secret in environments.yaml'),
        ])

    def test_no_admin_secret_found(self, mock_app, mock_open):
        # If admin-secret cannot be found anywhere a ProgramExit is called.
        mock_app.ProgramExit = app.ProgramExit
        mock_app.get_admin_secret = self.mock_get_admin_secret_error
        mock_app.bootstrap.return_value = (True, 'precise')
        options = self.make_options(
            admin_secret=None,
            env_name='local',
            env_file='environments.yaml')
        with self.assertRaises(app.ProgramExit) as context:
            manage.run(options)
        expected = (
            u'admin-secret not found in ~/.juju/environments/local.jenv '
            'or environments.yaml')
        self.assertEqual(expected, context.exception.message)
