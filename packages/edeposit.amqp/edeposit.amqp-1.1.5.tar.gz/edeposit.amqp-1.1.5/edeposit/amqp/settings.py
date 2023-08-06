# -*- coding: utf-8 -*-
"""
Configuration variables for the edeposit.amqp module.

For some reason, Sphinx wont list the variables in documentation (I've tried
it, really!), so you will have to look into source code.
"""

RABBITMQ_HOST = '127.0.0.1'
RABBITMQ_PORT = '5672'
RABBITMQ_USER_NAME = 'guest'
RABBITMQ_USER_PASSWORD = 'guest'

RABBITMQ_ALEPH_VIRTUALHOST = "aleph"
RABBITMQ_ALEPH_DAEMON_QUEUE = "daemon"
RABBITMQ_ALEPH_PLONE_QUEUE = "plone"
RABBITMQ_ALEPH_EXCHANGE = "search"
RABBITMQ_ALEPH_DAEMON_KEY = "request"
RABBITMQ_ALEPH_PLONE_KEY = "result"
RABBITMQ_ALEPH_EXCEPTION_KEY = "exception"
