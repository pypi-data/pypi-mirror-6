Run WSGI applications defined by paste.deploy configurations
************************************************************

.. contents::

A script, ``run-wsgi`` is provided that runs WSGI applications defined
in `Paste Deployment <http://pythonpaste.org/deploy/>`_ configuration
files.  For example, given a configuration file, ``paste.ini``::

  [app:main]
  use = egg:bobo
  bobo_resources = myapp

  [pipeline:debug]
  pipeline = debug reload main

  [filter:reload]
  use = egg:bobo#reload
  modules = zc.wsgirunner.tests

  [filter:debug]
  use = egg:bobo#debug

  [server:main]
  use = egg:waitress
  host = localhost
  port = 8080

  [configure:main]
  use = call:myapp:config
  key = 42

  [logging:main]
  log = INFO

We can run the applicaton with::

  run-wsgi paste.ini

If we want to run the debug pipeline::

  run-wsgi -a debug paste.ini

Logging and configuration
=========================

``zc.wsgirunner`` extends the Paste Deploy vocabulary of sections with
``logging`` and ``configuration`` sections.

As with the other sections, you can have multiple sections and select
which one you want with command-line options.

Logging sections
----------------

Logging sections come in 2 flavors, ZConfig, and basic.  If a logging
section has a ``config`` option, its value is passed `ZConfig's
<https://pypi.python.org/pypi/ZConfig>`_ [#zconfig]_ ``configureLoggers``
method. Otherwise, the options in the logging section are passed to
``logging.basicConfig``.

Configuration sections
----------------------

Configuration sections identify a configuration function with a
``use`` option, as with other Paste Deploy sections.  The
configuration object is called with global defaults and with options
from the configuration section.

Changes
*******

0.1.0 (2014-04-12)
==================

Initial release

.. [#zconfig]
    ZConfig provides the easiest way to create non-trivial logger
    configurations.

    Note, however, that ZConfig isn't a dependency of
    ``zc.wsgirunner``, so if you want to use ZConfig to configure
    logging, you need to install it separately.
