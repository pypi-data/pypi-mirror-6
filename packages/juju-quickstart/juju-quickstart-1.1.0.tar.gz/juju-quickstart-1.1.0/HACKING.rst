Juju Quickstart
===============

Juju Quickstart is a Juju plugin which allows for easily setting up a Juju
environment in very few steps. The environment is bootstrapped and set up so
that it can be managed using a Web interface (the Juju GUI).

Bundle deployments are also supported, and allow for setting up a complete
topology of services in one simple command.

Creating a development environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The development environment is created in a virtualenv. The environment
creation requires the *make*, *pip* and *virtualenv* programs to be installed.
To do that, run the following::

    $ make sysdeps

At this point, from the root of this branch, run the command::

    $ make

This command will create a ``.venv`` directory in the branch root, ignored
by DVCSes, containing the development virtual environment with all the
dependencies.

Testing and debugging the application
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Run the tests::

    $ make test

Run the tests and lint/pep8 checks::

    $ make check

Display help about all the available make targets, including instructions on
setting up and running the application in the development environment::

    $ make help

Installing the application
~~~~~~~~~~~~~~~~~~~~~~~~~~

To install Juju Quickstart in your local system, run the following::

    $ sudo make install

This command will take care of installing the requirements and the application
itself.

Running the application
~~~~~~~~~~~~~~~~~~~~~~~

juju-core will recognize Juju Quickstart as a plugin once the application is
installed by the command above. At this point, the application can be started
by running ``juju quickstart``.

Run the following for the list of all available options::

    $ juju quickstart --help

Assuming a Juju environment named ``local`` is properly configured in your
``~/.juju/environments.yaml`` file, here is an example invocation::

    $ juju quickstart -e local

If you have not installed the application using ``sudo make install``, as
described above, you can run it locally using the virtualenv's Python
installation::

    $ .venv/bin/python juju-quickstart --help

Creating PPA releases
~~~~~~~~~~~~~~~~~~~~~

The packaging repository (including the ``debian`` directory) can be checked
out from lp:~juju-gui/juju-quickstart/packaging/, e.g.::

    $ bzr branch lp:~juju-gui/juju-quickstart/packaging/ packaging
    $ cd packaging

Check that the packaging version reflects the latest Quickstart version. The
packaging version can be found in the ``debian/changelog`` file present in the
packaging branch root. To print the version of the current Quickstart, from the
juju-quickstart branch root, run the following::

    $ .venv/bin/python juju-quickstart --version

If the ``debian/changelog`` file is outdated, install the ``devscripts``
package and use ``dch`` to update the changelog, e.g.::

    $ sudo apt-get install devscripts
    $ dch -i  # Executed from the packaging branch root.

At this point, edit the changelog as required, commit and push the changes back
to the packaging branch trunk, and follow the instructions below.

The recipe for creating packages is in
<https://code.launchpad.net/~juju-gui-charmers/+recipe/juju-quickstart-daily>.
We currently publish beta releases on the Juju Quickstart Beta PPA: see
<https://launchpad.net/~juju-gui/+archive/quickstart-beta/+packages>.
When a beta release is ready to be published, we move over the packages from
the Juju Quickstart Beta PPA to the juju stable packages PPA in
<https://launchpad.net/~juju/+archive/stable>.

Packages depend on `python-jujuclient` and `python-websocket-client` to be
available. They are available in saucy, and they are also stored in our PPA in
order to support previous Ubuntu releases.

Creating PyPI releases
~~~~~~~~~~~~~~~~~~~~~~

Juju Quickstart is present on PyPI: see
<https://pypi.python.org/pypi/juju-quickstart>.
It is possible to register and upload a new release on PyPI by just running
``make release`` and providing your PyPI credentials.

Updating application and test dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Test dependencies are listed in the ``test-requirements.pip`` file in the
branch root, application ones in the ``requirements.pip`` file. The former
includes the latter, so any updates to the application requirements will also
update the test dependencies and therefore the testing virtual environment.
Note that, since the source requirements are dynamically generated parsing
``requirements.pip``, that file must only include PACKAGE==VERSION formatted
dependencies, and not other pip specific requirement specifications.

Also ensure, before updating the application dependencies, that those packages
are available in the main Ubuntu repositories for the series we support (from
precise to saucy), or in the Juju Quickstart Beta PPA: see
<https://launchpad.net/~juju-gui/+archive/quickstart-beta/+packages>.

Please also keep up to date the possible values for the environments.yaml
default-series field (see ``quickstart.settings.JUJU_DEFAULT_SERIES``) and the
set of series supported by the Juju GUI charm
(see ``quickstart.settings.JUJU_GUI_SUPPORTED_SERIES``).

Debugging bundle support
~~~~~~~~~~~~~~~~~~~~~~~~

When deploying a bundle, Quickstart just start the import process sending an
API request to the GUI charm builtin server, and then lets the user observe
the deployment process using the GUI.

Under the hood, a bundle deployment is executed by the GUI builtin server,
which in turn leverages the juju-deployer library. Since juju-deployer is not
asynchronous, the actual deployment is executed in a separate process.

Sometimes, when an error occurs, it is not obvious where to retrieve
information about what is going on. The GUI builtin server exposes some bundle
information in two places:

- https://<juju-gui-url>/gui-server-info displays in JSON format the current
  status of all scheduled/started/completed bundle deployments;
- /var/log/upstart/guiserver.log is the builtin server log file, which includes
  logs output from the juju-deployer library.

Moreover, setting `builtin-server-logging=debug` gives more debugging
information, e.g. it prints to the log the contents of the WebSocket messages
sent by the client (usually the Juju GUI) and by the Juju API server.
As mentioned, juju-deployer works on its own sandbox and uses its own API
connections, and for this reason the WebSocket traffic it generates is not
logged.

Sometimes, while debugging, it is convenient to restart the builtin server
(which also empties the bundle deployments queue). To do that, run the
following in the Juju GUI machine:

    service guiserver restart
