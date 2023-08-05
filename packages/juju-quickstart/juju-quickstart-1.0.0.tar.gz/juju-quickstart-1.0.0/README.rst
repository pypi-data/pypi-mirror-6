Juju Quickstart
===============

Juju Quickstart is an opinionated command-line tool that quickly starts Juju
and the GUI, whether you've never installed Juju or you have an existing Juju
environment running.

Features include the following:

* New users are guided, as needed, to install Juju, set up SSH keys, and
  configure it for first use.
* Juju environments can be created and managed from a command line interactive
  session.
* The Juju GUI is automatically installed, adding no additional machines
  (installing on an existing state server when possible).
* Bundles can be deployed, from local files, HTTP(S) URLs or the charm store,
  so that a complete topology of services can be set up in one simple command.
* Quickstart ends by opening the browser and automatically logging the user
  into the GUI, to observe and manage the environment visually.
* Users with a running Juju environment can run the quickstart command again to
  simply re-open the GUI without having to find the proper URL and password.

To install and start Juju Quickstart, run the following::

    juju-quickstart [-i]

Run ``juju-quickstart -h`` for a list of all the available options.

Once Juju has been installed, the command can also be run as a juju plugin,
without the hyphen (``juju quickstart``).
