Introduction
============

This module contains common parts shared with other AMQP modules from
edeposit project.

Installation
------------
Module is hosted at PYPI and can be easily installed:

    pip install edeposit.amqp

Sources can be found at github: https://github.com/jstavel/edeposit.amqp

Content
=======

Modules
-------

edeposit.amqp.settings
++++++++++++++++++++++

Configuration for RabbitMQ server and edeposit client modules connecting
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

Daemon providing AMQP communication with the `Aleph
module <https://github.com/jstavel/edeposit.amqp.aleph>`__.

edeposit/amqp/amqp\_tool.py
+++++++++++++++++++++++++++

Script for testing the communication and creating
exchanges/queues/routes in RabbitMQ.
