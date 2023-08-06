#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
# This work is licensed under a Creative Commons 3.0 Unported License
# (http://creativecommons.org/licenses/by/3.0/).
#
#= Imports ====================================================================
"""
Standalone daemon providing AMQP communication with
`Aleph module <https://github.com/jstavel/edeposit.amqp.aleph>`_.

This script can be used as aplication, not just as module::

    ./alephdaemon start/stop/restart [--foreground]

If ``--foreground`` parameter is used, script will not run as daemon, but as
normal script at foreground. Without that, only one (true unix) daemon instance
will be running at the time.
"""
import sys


import pika
import pikadaemon

try:
    from edeposit.amqp.aleph import *
    from edeposit.amqp.aleph.datastructures import *  # for serializers
except ImportError:
    from aleph import *
    from aleph.datastructures import *

try:
    import edeposit.amqp.serializers as serializers
except ImportError:
    import serializers

import settings


#= Functions & objects ========================================================
class AlephDaemon(pikadaemon.PikaDaemon):
    def onMessageReceived(self, method_frame, properties, body):
        # if UUID is not in headers, just ack the message and ignore it
        if "UUID" not in properties.headers:
            return True  # ack message

        try:
            reactToAMQPMessage(
                serializers.deserialize(body),
                self.sendResponse,
                properties.headers["UUID"]
            )
        except Exception, e:
            # get informations about message
            msg = e.message if hasattr(e, "message") else str(e)
            exception_type = str(e.__class__)
            exception_name = str(e.__class__.__name__)

            self.sendMessage(
                self.output_exchange,
                settings.RABBITMQ_ALEPH_EXCEPTION_KEY,
                str(e),
                properties=pika.BasicProperties(
                    content_type="application/text",
                    delivery_mode=2,
                    headers={
                        "exception": msg,
                        "exception_type": exception_type,
                        "exception_name": exception_name
                    }
                )
            )

        return True  # ack message

    def sendResponse(self, message, UUID):
        super(AlephDaemon, self).sendResponse(
            serializers.serialize(message),
            UUID
        )


def getConnectionParameters():
    """
    Returns:
        pika.ConnectionParameters: object set by variables from
        :class:`edeposit.amqp.settings`.
    """
    return pika.ConnectionParameters(
        host=settings.RABBITMQ_HOST,
        port=int(settings.RABBITMQ_PORT),
        virtual_host=settings.RABBITMQ_ALEPH_VIRTUALHOST,
        credentials=pika.PlainCredentials(
            settings.RABBITMQ_USER_NAME,
            settings.RABBITMQ_USER_PASSWORD
        )
    )


def main():
    """
    Arguments parsing, etc..
    """
    # initialize globals in `serializers` module (this is very important,
    # it won't have access to datastructures authomatically)
    serializers.init_globals(globals())

    daemon = AlephDaemon(
        connection_param=getConnectionParameters(),
        queue=settings.RABBITMQ_ALEPH_DAEMON_QUEUE,
        output_exchange=settings.RABBITMQ_ALEPH_EXCHANGE,
        output_key=settings.RABBITMQ_ALEPH_PLONE_KEY
    )

    if "--foreground" in sys.argv:  # run at foreground
        daemon.run()
    else:
        daemon.run_daemon()         # run as daemon


#= Main program ===============================================================
if __name__ == '__main__':
    main()
