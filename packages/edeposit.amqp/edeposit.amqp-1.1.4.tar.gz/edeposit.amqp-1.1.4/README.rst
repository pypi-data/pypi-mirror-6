Introduction
============

This module contains common parts shared with other AMQP modules from
`Edeposit <http://edeposit.nkp.cz/>`_ project. Main purpose is to provide
configuration data to AMQP server and generic daemons, to run the modules.    

Installation
------------
Module is hosted at `PYPI <http://pypi.python.org>`_, and can be easily 
installed using `PIP <http://en.wikipedia.org/wiki/Pip_%28package_manager%29>`_:

::

    pip install edeposit.amqp

Source code can be found at `GitHub <https://github.com/>`_: https://github.com/jstavel/edeposit.amqp

Content
=======
Content can be divided between generic modules to support AMQP communcation and scripts, which provides ability to testn and tweak AMQP communication.

Modules
-------

edeposit.amqp.settings
++++++++++++++++++++++

Configuration for RabbitMQ server and Edeposit client modules connecting
into it.

edeposit.amqp.daemonwrapper
+++++++++++++++++++++++++++

Class for spawning true unix daemons.

edeposit.amqp.pikadaemon
++++++++++++++++++++++++

Generic AMQP blocking communication daemon server.

Scripts
-------

edeposit/amqp/alephdaemon.py
++++++++++++++++++++++++++++

Daemon providing AMQP communication with the `edeposit.amqp.aleph <https://github.com/jstavel/edeposit.amqp.aleph>`_ module.

edeposit/amqp/amqp\_tool.py
+++++++++++++++++++++++++++

Script for testing the communication and creating
exchanges/queues/routes in `RabbitMQ <https://www.rabbitmq.com/>`_.

Acceptance tests
================
`Robot Framework <http://robotframework.org/>`__ is used to test the code.
You can find the tests in ``src/edeposit/amqp/aleph/tests`` directory.

Tests can be invoked manually (from the root of the package):

::

    $ pybot -W 80 --pythonpath edeposit/amqp/tests/:src edeposit/amqp/tests/; (cd docs/; make html)

Or continuously using nosier:

::

    $ nosier -p edeposit -b 'export' "pybot -W 80 --pythonpath edeposit/amqp/tests/:src edeposit/amqp/tests/; (cd docs/; make html)"