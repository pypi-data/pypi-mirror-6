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

"""Juju Quickstart application management."""

from __future__ import (
    print_function,
    unicode_literals,
)

import argparse
import codecs
import logging
import os
import shutil
import sys
import webbrowser

import quickstart
from quickstart import (
    app,
    settings,
    utils,
)
from quickstart.cli import views
from quickstart.models import (
    charms,
    envs,
)


version = quickstart.get_version()


class _DescriptionAction(argparse.Action):
    """A customized argparse action that just shows a description."""

    def __call__(self, parser, *args, **kwargs):
        print(settings.DESCRIPTION)
        parser.exit()


def _validate_bundle(options, parser):
    """Validate and process the bundle options.

    Populate the options namespace with the following names:
        - bundle_name: the name of the bundle;
        - bundle_services: a list of service names included in the bundle;
        - bundle_yaml: the YAML encoded contents of the bundle.
        - bundle_id: the bundle_id in Charmworld.  None if not a 'bundle:' URL.
    Exit with an error if the bundle options are not valid.
    """
    bundle = options.bundle
    bundle_id = None
    if bundle.startswith('bundle:'):
        # Convert "bundle:" URLs into HTTPS ones. The next if block below will
        # then load the bundle contents from the remote location.
        try:
            bundle, bundle_id = utils.convert_bundle_url(bundle)
        except ValueError as err:
            return parser.error('unable to open the bundle: {}'.format(err))
    if bundle.startswith('http://') or bundle.startswith('https://'):
        # Load the bundle from a remote URL.
        try:
            bundle_yaml = utils.urlread(bundle)
        except IOError as err:
            return parser.error('unable to open bundle URL: {}'.format(err))
    else:
        # Load the bundle from a file.
        bundle_file = os.path.abspath(os.path.expanduser(bundle))
        if os.path.isdir(bundle_file):
            bundle_file = os.path.join(bundle_file, 'bundles.yaml')
        try:
            bundle_yaml = codecs.open(
                bundle_file.encode('utf-8'), encoding='utf-8').read()
        except IOError as err:
            return parser.error('unable to open bundle file: {}'.format(err))
    # Validate the bundle.
    try:
        bundle_name, bundle_services = utils.parse_bundle(
            bundle_yaml, options.bundle_name)
    except ValueError as err:
        return parser.error(bytes(err))
    # Update the options namespace with the new values.
    options.bundle_name = bundle_name
    options.bundle_services = bundle_services
    options.bundle_yaml = bundle_yaml
    options.bundle_id = bundle_id


def _validate_charm_url(options, parser):
    """Validate the provided charm URL option.

    Exit with an error if:
        - the URL is not a valid charm URL;
        - the URL represents a local charm;
        - the charm series is not supported;
        - a bundle deployment has been requested but the provided charm does
          not support bundles.

    Leave the options namespace untouched.
    """
    try:
        charm = charms.Charm.from_url(options.charm_url)
    except ValueError as err:
        return parser.error(bytes(err))
    if charm.is_local():
        return parser.error(b'local charms are not allowed: {}'.format(charm))
    if charm.series not in settings.JUJU_GUI_SUPPORTED_SERIES:
        return parser.error(
            'unsupported charm series: {}'.format(charm.series))
    if (
        # The user requested a bundle deployment.
        options.bundle and
        # This is the official Juju GUI charm.
        charm.name == settings.JUJU_GUI_CHARM_NAME and
        not charm.user and
        # The charm at this revision does not support bundle deployments.
        charm.revision < settings.MINIMUM_CHARM_REVISION_FOR_BUNDLES
    ):
        return parser.error(
            'bundle deployments not supported by the requested charm '
            'revision: {}'.format(charm))


def _retrieve_env_db(parser, env_file=None):
    """Retrieve the environment database (or create an in-memory empty one)."""
    if env_file is None:
        return envs.create_empty_env_db()
    try:
        return envs.load(env_file)
    except ValueError as err:
        return parser.error(bytes(err))


def _create_save_callable(parser, env_file):
    """Return a function that can be used to save an env_db to the env_file.

    The returned function is used as save_callable by the environments
    management views.

    The resulting function uses the given parser instance to exit the
    application with an error if an OSError exception is raised while saving
    the environments database.
    """
    backup_function = utils.run_once(shutil.copyfile)

    def save_callable(env_db):
        try:
            envs.save(env_file, env_db, backup_function=backup_function)
        except OSError as err:
            return parser.error(bytes(err))

    return save_callable


def _start_interactive_session(parser, env_type_db, env_db, env_file):
    """Start the Urwid interactive session.

    Return the env_data corresponding to the user selected environment.
    Exit the application if the user exits the interactive session without
    selecting an environment to start.
    """
    save_callable = _create_save_callable(parser, env_file)
    new_env_db, env_data = views.show(
        views.env_index, env_type_db, env_db, save_callable)
    if new_env_db != env_db:
        print('changes to the environments file have been saved')
    if env_data is None:
        # The user exited the interactive session without selecting an
        # environment to start: this means this was just an environment
        # editing session and we can just quit now.
        return sys.exit('quitting')
    return env_data


def _retrieve_env_data(parser, env_type_db, env_db, env_name):
    """Retrieve and return the env_data corresponding to the given env_name.

    Invoke a parser error if the environment does not exist or is not valid.
    """
    try:
        env_data = envs.get_env_data(env_db, env_name)
    except ValueError as err:
        # The specified environment does not exist.
        return parser.error(bytes(err))
    env_metadata = envs.get_env_metadata(env_type_db, env_data)
    errors = envs.validate(env_metadata, env_data)
    if errors:
        msg = 'cannot use the {} environment:\n{}'.format(
            env_name, '\n'.join(errors.values()))
        return parser.error(msg.encode('utf-8'))
    return env_data


def _setup_env(options, parser):
    """Set up, validate and process the provided environment related options.

    Also start the environments management interactive session if required.

    Exit with an error if options are not valid.
    """
    logging.debug('setting up juju environments')
    env_name = options.env_name
    env_file = os.path.abspath(os.path.expanduser(options.env_file))
    interactive = options.interactive
    env_file_exists = os.path.exists(env_file)
    if not env_file_exists:
        # If the Juju home is not set up, force the interactive mode and ignore
        # the user provided env name.
        interactive = True
        env_name = None
    # Validate the environment name.
    if env_name is None and not interactive:
        # The user forced non-interactive mode but a default env name cannot
        # be retrieved. In this case, just exit with an error.
        return parser.error(
            'unable to find an environment name to use\n'
            'It is possible to specify the environment to use by either:\n'
            '  - selecting one from the quickstart interactive session,\n'
            '    i.e. juju quickstart -i;\n'
            '  - passing the -e or --environment argument;\n'
            '  - setting the JUJU_ENV environment variable;\n'
            '  - using "juju switch" to select the default environment;\n'
            '  - setting the default environment in {}.'.format(env_file)
        )

    # Retrieve the environment database (or create an in-memory empty one).
    env_db = _retrieve_env_db(parser, env_file if env_file_exists else None)

    # Validate the environment.
    env_type_db = envs.get_env_type_db()
    if interactive:
        # Start the interactive session.
        env_data = _start_interactive_session(
            parser, env_type_db, env_db, env_file)
    else:
        # This is a non-interactive session and we need to validate the
        # selected environment before proceeding.
        env_data = _retrieve_env_data(parser, env_type_db, env_db, env_name)
    # Update the options namespace with the new values.
    options.admin_secret = env_data.get('admin-secret')
    options.env_file = env_file
    options.env_name = env_data['name']
    options.env_type = env_data['type']
    options.default_series = env_data.get('default-series')
    options.interactive = interactive


def _configure_logging(level):
    """Set up the application logging."""
    root = logging.getLogger()
    # Remove any previous handler on the root logger.
    for handler in root.handlers[:]:
        root.removeHandler(handler)
    logging.basicConfig(
        level=level,
        format=(
            '%(asctime)s %(levelname)s '
            '%(module)s@%(funcName)s:%(lineno)d '
            '%(message)s'
        ),
        datefmt='%H:%M:%S',
    )


def _convert_options_to_unicode(options):
    """Convert all byte string values in the options namespace to unicode.

    Modify the options in place and return None.
    """
    encoding = sys.stdin.encoding or 'utf-8'
    for key, value in options._get_kwargs():
        if isinstance(value, bytes):
            setattr(options, key, value.decode(encoding))


def setup():
    """Set up the application options and logger.

    Return the options as a namespace containing the following attributes:
        - admin_secret: the password to use to access the Juju API or None if
          no admin-secret is present in the $JUJU_HOME/environment.yaml file;
        - bundle: the optional bundle (path or URL) to be deployed;
        - charm_url: the Juju GUI charm URL or None if not specified;
        - debug: whether debug mode is activated;
        - env_file: the absolute path of the Juju environments.yaml file;
        - env_name: the name of the Juju environment to use;
        - env_type: the provider type of the selected Juju environment;
        - interactive: whether to start the interactive session;
        - open_browser: whether the GUI browser must be opened.

    The following attributes will also be included in the namespace if a bundle
    deployment is requested:
        - bundle_name: the name of the bundle to be deployed;
        - bundle_services: a list of service names included in the bundle;
        - bundle_yaml: the YAML encoded contents of the bundle.
        - bundle_id: the Charmworld identifier for the bundle if a
            'bundle:' URL is provided.

    Exit with an error if the provided arguments are not valid.
    """
    default_env_name = envs.get_default_env_name()
    # Define the help message for the --environment option.
    env_help = 'The name of the Juju environment to use'
    if default_env_name is not None:
        env_help = '{} (%(default)s)'.format(env_help)
    # Create and set up the arguments parser.
    parser = argparse.ArgumentParser(description=quickstart.__doc__)
    parser.add_argument(
        'bundle', default=None, nargs='?',
        help='The optional bundle to be deployed. The bundle can be '
             '1) a fully qualified bundle URL (starting with "bundle:"), '
             '2) a URL ("http:" or "https:") to a YAML/JSON, '
             '3) a path to a YAML/JSON file, or '
             '4) a path to a directory containing a "bundles.yaml" file')
    parser.add_argument(
        '-e', '--environment', default=default_env_name, dest='env_name',
        help=env_help)
    parser.add_argument(
        '-n', '--bundle-name', default=None, dest='bundle_name',
        help='The name of the bundle to use. This must be included in the '
             'provided bundle YAML/JSON. Specifying the bundle name is not '
             'required if the bundle YAML/JSON only contains one bundle. This '
             'option is ignored if the bundle file is not specified')
    parser.add_argument(
        '-i', '--interactive', action='store_true', dest='interactive',
        help='Start the environments management interactive session')
    parser.add_argument(
        '--environments-file', dest='env_file',
        default=os.path.join(settings.JUJU_HOME, 'environments.yaml'),
        help='The path to the Juju environments YAML file (%(default)s)')
    parser.add_argument(
        '--gui-charm-url', dest='charm_url',
        help='The Juju GUI charm URL to deploy in the environment. If not '
             'provided, the last release of the GUI will be deployed. The '
             'charm URL must include the charm version, e.g. '
             'cs:~juju-gui/precise/juju-gui-116. This option is ignored if '
             'Juju GUI is already present in the environment')
    parser.add_argument(
        '--no-browser', action='store_false', dest='open_browser',
        help='Avoid opening the browser to the GUI at the end of the process')
    parser.add_argument(
        '--version', action='version', version='%(prog)s {}'.format(version))
    parser.add_argument(
        '--debug', action='store_true',
        help='Turn debug mode on. When enabled, all the subcommands and API '
             'calls are logged to stdout, and the Juju environment is '
             'bootstrapped passing --debug')
    # This is required by juju-core: see "juju help plugins".
    parser.add_argument(
        '--description', action=_DescriptionAction, default=argparse.SUPPRESS,
        nargs=0, help="Show program's description and exit")
    # Parse the provided arguments.
    options = parser.parse_args()
    # Convert the provided string arguments to unicode.
    _convert_options_to_unicode(options)
    # Validate and process the provided arguments.
    _setup_env(options, parser)
    if options.bundle is not None:
        _validate_bundle(options, parser)
    if options.charm_url is not None:
        _validate_charm_url(options, parser)
    # Set up logging.
    _configure_logging(logging.DEBUG if options.debug else logging.INFO)
    return options


def run(options):
    """Run the application."""
    print('juju quickstart v{}'.format(version))
    logging.debug('ensuring juju and lxc are installed')
    app.ensure_dependencies()
    logging.debug('ensuring SSH keys are available')
    app.ensure_ssh_keys()
    print('bootstrapping the {} environment (type: {})'.format(
        options.env_name, options.env_type))
    is_local = options.env_type == 'local'
    requires_sudo = app.bootstrap_requires_sudo(is_local)
    already_bootstrapped, bsn_series = app.bootstrap(
        options.env_name, requires_sudo=requires_sudo, debug=options.debug)

    # Retrieve the admin-secret for the current environment.
    try:
        admin_secret = app.get_admin_secret(
            options.env_name, settings.JUJU_HOME)
    except ValueError as err:
        admin_secret = options.admin_secret
        if admin_secret is None:
            # The admin-secret cannot be found in the jenv file and is not
            # explicitly specified in the environments.yaml file.
            msg = b'{} or {}'.format(err, options.env_file.encode('utf-8'))
            raise app.ProgramExit(msg)

    print('retrieving the Juju API address')
    api_url = app.get_api_url(options.env_name)
    print('connecting to {}'.format(api_url))
    env = app.connect(api_url, admin_secret)

    # It is not possible to deploy on the bootstrap node if we are using the
    # local provider, or if the bootstrap node series is not compatible with
    # the Juju GUI charm.
    machine = '0'
    if is_local or (bsn_series != settings.JUJU_GUI_PREFERRED_SERIES):
        machine = None
    unit_name = app.deploy_gui(
        env, settings.JUJU_GUI_SERVICE_NAME, machine,
        charm_url=options.charm_url, check_preexisting=already_bootstrapped)
    address = app.watch(env, unit_name)
    env.close()
    url = 'https://{}'.format(address)
    print('url: {}\npassword: {}'.format(url, admin_secret))
    gui_api_url = 'wss://{}:443/ws'.format(address)
    print('connecting to the Juju GUI server')
    gui_env = app.connect(gui_api_url, admin_secret)

    # Handle bundle deployment.
    if options.bundle is not None:
        services = ', '.join(options.bundle_services)
        print('requesting a deployment of the {} bundle with the following '
              'services:\n  {}'.format(options.bundle_name, services))
        # We need to connect to an API WebSocket server supporting bundle
        # deployments. The GUI builtin server, listening on the Juju GUI
        # address, exposes an API suitable for deploying bundles.
        app.deploy_bundle(
            gui_env, options.bundle_yaml, options.bundle_name,
            options.bundle_id)
        print('bundle deployment request accepted')

    if options.open_browser:
        token = app.create_auth_token(gui_env)
        if token is not None:
            url += '/?authtoken={}'.format(token)
        webbrowser.open(url)
    gui_env.close()
    print(
        'done!\n\n'
        'Run "juju quickstart -e {env_name}" again if you want\n'
        'to reopen and log in to the GUI browser later.\n'
        'Run "juju quickstart -i" if you want to manage\n'
        'or bootstrap your Juju environments using the\n'
        'interactive session.\n'
        'Run "{sudo}juju destroy-environment {eflag}{env_name} [-y]"\n'
        'to destroy the environment you just bootstrapped.'.format(
            env_name=options.env_name,
            sudo='sudo ' if requires_sudo else '',
            eflag='-e ' if requires_sudo else '')
    )
