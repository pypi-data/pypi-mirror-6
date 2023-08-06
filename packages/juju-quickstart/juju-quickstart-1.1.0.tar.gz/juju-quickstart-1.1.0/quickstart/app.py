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

"""Juju Quickstart base application functions."""

from __future__ import (
    print_function,
    unicode_literals,
)

import json
import logging
import os
import sys
import time

import jujuclient

from quickstart import (
    juju,
    settings,
    utils,
    watchers,
)
from quickstart.models import envs


class ProgramExit(Exception):
    """An error occurred while setting up the Juju environment.

    Raise this exception if you want the program to exit gracefully printing
    the error message to stderr.

    The error message can be either a unicode or a byte string.
    """

    def __init__(self, message):
        if isinstance(message, unicode):
            message = message.encode('utf-8')
        self.message = message

    def __str__(self):
        return b'juju-quickstart: error: {}'.format(self.message)


def ensure_dependencies():
    """Ensure that Juju and LXC are installed.

    If juju is not found in the PATH, then add the juju stable PPA and install
    both juju and lxc.

    Return when juju is available.
    Raise a ProgramExit if an error occurs installing.
    """
    required_packages = []
    retcode = utils.call('/usr/bin/juju', 'version')[0]
    if retcode > 0:
        required_packages.append('juju-core')
    retcode = utils.call('/usr/bin/lxc-ls')[0]
    if retcode > 0:
        # The lxc package is required to create the LXC containers used by
        # the local provider. When the local provider is enabled, the host
        # itself is used as bootstrap node. For this reason, the mongodb-server
        # package from the Juju stable PPA is also required.
        required_packages.extend(['lxc', 'mongodb-server'])
    if required_packages:
        try:
            utils.add_apt_repository('ppa:juju/stable')
        except OSError as err:
            raise ProgramExit(bytes(err))
        print('installing the following packages: {} '
              '(this can take a while)'.format(', '.join(required_packages)))
        print('sudo privileges will be used for package installation')
        retcode, _, error = utils.call(
            'sudo', '/usr/bin/apt-get', 'install', '-y', *required_packages)
        if retcode:
            raise ProgramExit(error)


def ensure_ssh_keys():
    """Ensure that SSH keys are available.

    Allow the user to let quickstart create SSH keys, or quit by raising a
    ProgramExit if they would like to create the key themselves.
    """
    # Test to see if we have ssh-keys loaded into the ssh-agent, or if we can
    # add them to the currently running ssh-agent.
    if check_ssh_keys():
        return

    # No responsive agent was found.  Start one up.
    try:
        utils.start_ssh_agent()
    except OSError as err:
        raise ProgramExit(bytes(err))

    # And now check again.
    if not check_ssh_keys():
        print('Warning: No SSH keys were found in ~/.ssh\n\n'
              'To proceed and generate keys, quickstart can\n\n'
              '[a] automatically create keys for you\n'
              '[m] provide commands to manually create your keys\n\n'
              'Note:\nssh-keygen will prompt you for an optional '
              'passphrase to generate your key for\nyou. '
              'Quickstart does not store it.\n')

        create_keys = ''
        try:
            create_keys = raw_input('Automatically create keys [a], '
                                    'manually create the keys [m], or cancel '
                                    '[C]? ')
        except KeyboardInterrupt:
            pass
        if create_keys.lower() == 'a':
            create_ssh_keys()
        elif create_keys.lower() == 'm':
            watch_for_ssh_keys()
        else:
            msg = 'If you would like to create the keys yourself, ' \
                  'please run this command, follow its ' \
                  'instructions, and then re-run quickstart:\n\n' \
                  '  ssh-keygen -b 4096 -t rsa'
            sys.exit(msg)


def check_ssh_keys():
    """Check whether or not ssh keys exist and are loaded by the agent.

    Raise a program exit if we can't load the keys because they're broken
    in some way.

    Return true if there are ssh identities loaded and available in an agent,
    false otherwise.
    """
    no_keys_msg = 'The agent has no identities.\n'
    retcode, output, _ = utils.call('/usr/bin/ssh-add', '-l')
    if retcode == 0:
        # We have keys and an agent.
        return True
    elif retcode == 1 and output == no_keys_msg:
        # We have an agent, but no keys currently loaded.
        retcode, output, error = utils.call('/usr/bin/ssh-add')
        if retcode == 0:
            # We were able to load an identity
            return True
        elif retcode == 1:
            # If ssh-add is called without -l and there are no identities
            # available, there will be no output or error, but retcode will
            # still be 1.
            return False
        else:
            # We weren't able to load keys for some other reason, such as being
            # readable by group or world, or malformed.
            msg = 'error attempting to add ssh keys! {}'
            raise ProgramExit(msg.format(error).encode('utf-8'))
    return False


def watch_for_ssh_keys():
    """Watch for generation of ssh keys from another terminal or window.

    This will run until keys become visible to quickstart or killed by
    the user.
    """
    print('Please run this command in another terminal or window and '
          'follow the\ninstructions it produces; quickstart will '
          'continue when keys are\ngenerated, or ^C to quit.\n\n'
          '  ssh-keygen -b 4096 -t rsa\n\nWaiting...')
    try:
        while not check_ssh_keys():
            # Print and flush the buffer immediately; an empty end kwarg will
            # not cause the buffer to flush until after a certain number of
            # bytes.
            print('.', end='')
            sys.stdout.flush()
            time.sleep(3)
    except KeyboardInterrupt:
        sys.exit('\nquitting')


def create_ssh_keys():
    """Create SSH keys for the user

    Raises ProgramExit if the keys were not created successfully.

    NB: this involves user interaction for entering the passphrase; this may
    have to change if creating SSH keys takes place in the urwid interface.
    """
    key_file = os.path.join(os.path.expanduser('~'), '.ssh', 'id_rsa')
    print('generating new ssh key...')
    retcode, _, error = utils.call('/usr/bin/ssh-keygen',
                                   '-q',  # silent
                                   '-b', '4096',  # 4096 bytes
                                   '-t', 'rsa',  # RSA type
                                   '-C', 'Generated with Juju Quickstart',
                                   '-f', key_file)
    if retcode:
        raise ProgramExit('error generating ssh key!  {}'.format(error))
    print('adding key to ssh-agent...')
    retcode, _, error = utils.call('/usr/bin/ssh-add')
    if retcode:
        raise ProgramExit('error adding key to agent!  {}'.format(error))
    print('a new ssh key was generated in {}'.format(key_file))


def bootstrap_requires_sudo(is_local):
    """Return True if "sudo" is required to bootstrap the Juju environment.

    Return False otherwise.
    Raise a ProgramExit if any error occurs retrieving the Juju version.
    """
    if not is_local:
        return False
    # If this is a local environment, notify the user that "sudo" will be
    # required to bootstrap the application, even in newer Juju versions where
    # "sudo" is invoked by juju-core itself.
    print('sudo privileges required to bootstrap the environment')
    # If the Juju core version is less than 1.17.2 then use sudo for local
    # deployments.
    try:
        major, minor, patch = utils.get_juju_version()
    except ValueError as err:
        raise ProgramExit(bytes(err))
    return (major, minor, patch) < (1, 17, 2)


def bootstrap(env_name, requires_sudo=False, debug=False):
    """Bootstrap the Juju environment with the given name.

    Do not bootstrap the environment if already bootstrapped.

    Return a tuple (already_bootstrapped, series) in which:
        - already_bootstrapped indicates whether the environment was already
          bootstrapped;
        - series is the bootstrap node Ubuntu series.

    The is_local argument indicates whether the environment is configured to
    use the local provider. If so, sudo privileges are requested in order to
    bootstrap the environment.

    If debug is True and the environment not bootstrapped, execute the
    bootstrap command passing the --debug flag.

    Raise a ProgramExit if any error occurs in the bootstrap process.
    """
    already_bootstrapped = False
    cmd = ['/usr/bin/juju', 'bootstrap', '-e', env_name]
    if requires_sudo:
        cmd.insert(0, 'sudo')
    if debug:
        cmd.append('--debug')
    retcode, _, error = utils.call(*cmd)
    if retcode:
        # XXX frankban 2013-11-13 bug 1252322: the check below is weak. We are
        # relying on an error message in order to decide if the environment is
        # already bootstrapped. Other possibilities include checking if the
        # jenv file is present (in ~/.juju/environments/) and, if so, check the
        # juju status. Unfortunately this is also prone to errors, because a
        # jenv file can be there but the environment not really bootstrapped or
        # functional (e.g. sync-tools was used, or a previous bootstrap failed,
        # or the user terminated machines from the ec2 panel, etc.). Moreover
        # jenv files seems to be an internal juju-core detail. Definitely we
        # need to find a better way, but for now the "asking forgiveness"
        # approach feels like the best compromise we have. Also note that,
        # rather than comparing the expected error with the obtained one, we
        # search in the error in order to support bootstrap --debug.
        if 'environment is already bootstrapped' not in error:
            # We exit if the error is not "already bootstrapped".
            raise ProgramExit(error)
        # Juju is bootstrapped, but we don't know if it is ready yet. Fall
        # through to the next block for that check.
        already_bootstrapped = True
        print('reusing the already bootstrapped {} environment'.format(
            env_name))
    # Call "juju status" multiple times until the bootstrap node is ready.
    # Exit with an error if the agent is not ready after ten minutes.
    # Note: when using the local provider, calling "juju status" is very fast,
    # but e.g. on ec2 the first call (right after "bootstrap") can take
    # several minutes, and subsequent calls are relatively fast (seconds).
    print('retrieving the environment status')
    timeout = time.time() + (60*10)
    while time.time() < timeout:
        retcode, output, error = utils.call(
            '/usr/bin/juju', 'status', '-e', env_name, '--format', 'yaml')
        if retcode:
            continue
        # Ensure the state server is up and the agent is started.
        try:
            agent_state = utils.get_agent_state(output)
        except ValueError:
            continue
        if agent_state == 'started':
            series = utils.get_bootstrap_node_series(output)
            return already_bootstrapped, series
        # If the agent is in an error state, there is nothing we can do, and
        # it's not useful to keep trying.
        if agent_state == 'error':
            raise ProgramExit('state server failure:\n{}'.format(output))
    details = ''.join(filter(None, [output, error])).strip()
    raise ProgramExit('the state server is not ready:\n{}'.format(details))


def get_admin_secret(env_name, juju_home):
    """Read the admin-secret from the generated environment file.

    At bootstrap, juju (v1.16 and later) writes the admin-secret to a
    generated file located in JUJU_HOME.  Return the value.
    Raise a ValueError if:
        - the environment file is not found;
        - the environment file contents are not parsable by YAML;
        - the YAML contents are not properly structured;
        - the admin-secret is not found.
    """
    filename = '{}.jenv'.format(env_name)
    juju_env_file = os.path.expanduser(
        os.path.join(juju_home, 'environments', filename))
    jenv_db = envs.load_generated(juju_env_file)
    try:
        return jenv_db['admin-secret']
    except KeyError:
        msg = 'admin-secret not found in {}'.format(juju_env_file)
        raise ValueError(msg.encode('utf-8'))


def get_api_url(env_name):
    """Return a Juju API URL for the given environment name.

    Use the Juju CLI in a subprocess in order to retrieve the API addresses.
    Return the complete URL, e.g. "wss://api.example.com:17070".
    Raise a ProgramExit if any error occurs.
    """
    retcode, output, error = utils.call(
        '/usr/bin/juju', 'api-endpoints', '-e', env_name, '--format', 'json')
    if retcode:
        raise ProgramExit(error)
    # Assuming there is always at least one API address, grab the first one
    # from the JSON output.
    api_address = json.loads(output)[0]
    return 'wss://{}'.format(api_address)


def connect(api_url, admin_secret):
    """Connect to the Juju API server and log in using the given credentials.

    Return a connected and authenticated Juju Environment instance.
    Raise a ProgramExit if any error occurs while establishing the WebSocket
    connection or if the API returns an error response.
    """
    try_count = 0
    while True:
        try:
            env = juju.connect(api_url)
        except Exception as err:
            try_count += 1
            msg = b'unable to connect to the Juju API server on {}: {}'.format(
                api_url.encode('utf-8'), err)
            if try_count >= 30:
                raise ProgramExit(msg)
            else:
                logging.warn('Retrying: ' + msg)
                time.sleep(1)
        else:
            break
    try:
        env.login(admin_secret)
    except jujuclient.EnvError as err:
        msg = 'unable to log in to the Juju API server on {}: {}'
        raise ProgramExit(msg.format(api_url, err.message))
    return env


def create_auth_token(env):
    """Return a new authentication token.

    If the server does not support the request, return None.  Raise any other
    error."""
    try:
        result = env.create_auth_token()
    except jujuclient.EnvError as err:
        if err.message == 'unknown object type "GUIToken"':
            # This is a legacy charm.
            return None
        else:
            raise
    return result['Token']


def deploy_gui(
        env, service_name, machine, charm_url=None, check_preexisting=False):
    """Deploy and expose the given service, reusing the bootstrap node.

    Only deploy the service if not already present in the environment.
    Do not add a unit to the service if the unit is already there.

    Receive an authenticated Juju Environment instance, the name of the
    service, the machine where to deploy to (or None for a new machine),
    the optional Juju GUI charm URL (e.g. cs:~juju-gui/precise/juju-gui-42),
    and a flag (check_preexisting) that can be set to True in order to make
    the function check for a pre-existing service and/or unit.

    If the charm URL is not provided, and the service is not already deployed,
    the function tries to retrieve it from charmworld. In this case a default
    charm URL is used if charmworld is not available.

    Return the name of the first running unit belonging to the given service.
    Raise a ProgramExit if the API server returns an error response.
    """
    service_data, unit_data = None, None
    if check_preexisting:
        # The service and/or the unit can be already in the environment.
        try:
            status = env.get_status()
        except jujuclient.EnvError as err:
            raise ProgramExit('bad API response: {}'.format(err.message))
        service_data, unit_data = utils.get_service_info(status, service_name)
    if service_data is None:
        # The service does not exist in the environment.
        print('requesting {} deployment'.format(service_name))
        if charm_url is None:
            try:
                charm_url = utils.get_charm_url()
            except (IOError, ValueError) as err:
                msg = 'unable to retrieve the {} charm URL from the API: {}'
                logging.warn(msg.format(service_name, err))
                charm_url = settings.DEFAULT_CHARM_URL
        utils.check_gui_charm_url(charm_url)
        # Deploy the service without units.
        try:
            env.deploy(service_name, charm_url, num_units=0)
        except jujuclient.EnvError as err:
            raise ProgramExit('bad API response: {}'.format(err.message))
        print('{} deployment request accepted'.format(service_name))
        service_exposed = False
    else:
        # We already have the service in the environment.
        print('service {} already deployed'.format(service_name))
        utils.check_gui_charm_url(service_data['CharmURL'])
        service_exposed = service_data.get('Exposed', False)
    # At this point the service is surely deployed in the environment: expose
    # it if necessary and add a unit if it is missing.
    if not service_exposed:
        print('exposing service {}'.format(service_name))
        try:
            env.expose(service_name)
        except jujuclient.EnvError as err:
            raise ProgramExit('bad API response: {}'.format(err.message))
    if unit_data is None:
        # Add a unit to the service.
        print('requesting new unit deployment')
        try:
            response = env.add_unit(service_name, machine_spec=machine)
        except jujuclient.EnvError as err:
            raise ProgramExit('bad API response: {}'.format(err.message))
        unit_name = response['Units'][0]
        print('{} deployment request accepted'.format(unit_name))
    else:
        # A service unit is already present in the environment. Go ahead
        # and try to reuse that unit.
        unit_name = unit_data['Name']
        print('reusing unit {}'.format(unit_name))
    return unit_name


def watch(env, unit_name):
    """Start watching the given unit and the machine the unit belongs to.

    Output a human readable message each time a relevant change is found.

    The following changes are considered relevant for a healthy unit:
        - the machine is pending;
        - the unit is pending;
        - the machine is started;
        - the unit is reachable;
        - the unit is installed;
        - the unit is started.

    Stop watching and return the unit public address when the unit is started.
    Raise a ProgramExit if the API server returns an error response, or if
    either the service unit or the machine is removed or in error.
    """
    address = unit_status = machine_id = machine_status = ''
    watcher = env.watch_changes(watchers.unit_machine_changes)
    while True:
        try:
            unit_changes, machine_changes = watcher.next()
        except jujuclient.EnvError as err:
            raise ProgramExit(
                'bad API server response: {}'.format(err.message))
        # Process unit changes:
        for action, data in unit_changes:
            if data['Name'] == unit_name:
                try:
                    data = watchers.parse_unit_change(
                        action, data, unit_status, address)
                except ValueError as err:
                    raise ProgramExit(bytes(err))
                unit_status, address, machine_id = data
                if address and unit_status == 'started':
                    # We can exit this loop.
                    return address
                # The mega-watcher contains a single change for each specific
                # unit. For this reason, we can exit the for loop here.
                break
        if not machine_id:
            # No need to process machine changes: we still don't know what
            # machine the unit belongs to.
            continue
        # Process machine changes.
        for action, data in machine_changes:
            if data['Id'] == machine_id:
                try:
                    machine_status = watchers.parse_machine_change(
                        action, data, machine_status)
                except ValueError as err:
                    raise ProgramExit(bytes(err))
                # The mega-watcher contains a single change for each specific
                # machine. For this reason, we can exit the for loop here.
                break


def deploy_bundle(env, bundle_yaml, bundle_name, bundle_id):
    """Deploy a bundle.

    Receive an API URL to a WebSocket server supporting bundle deployments, the
    admin_secret to use in the authentication process, the bundle YAML encoded
    contents and the bundle name to be imported.

    Raise a ProgramExit if the API server returns an error response.
    """
    try:
        env.deploy_bundle(bundle_yaml, name=bundle_name, bundle_id=bundle_id)
    except jujuclient.EnvError as err:
        raise ProgramExit('bad API server response: {}'.format(err.message))
