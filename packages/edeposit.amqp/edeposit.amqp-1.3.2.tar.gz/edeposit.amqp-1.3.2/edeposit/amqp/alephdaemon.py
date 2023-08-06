#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
#= Imports ====================================================================
"""
Standalone daemon providing AMQP communication with
`Aleph module <https://github.com/jstavel/edeposit.amqp.aleph>`_.

This script can be used as aplication, not just as module::

    ./alephdaemon.py start/stop/restart [--foreground]

If ``--foreground`` parameter is used, script will not run as daemon, but as
normal script at foreground. Without that, only one (true unix) daemon instance
will be running at the time.
"""
import sys

from amqpdaemon import AMQPDaemon, getConParams


try:
    from edeposit.amqp.aleph import *
    from edeposit.amqp.aleph.datastructures import *  # for serializers
except ImportError:
    from aleph import *
    from aleph.datastructures import *

import settings


#= Functions & objects ========================================================
def main():
    """
    Arguments parsing, etc..
    """
    daemon = AMQPDaemon(
        con_param=getConParams(
            settings.RABBITMQ_ALEPH_VIRTUALHOST
        ),
        queue=settings.RABBITMQ_ALEPH_INPUT_QUEUE,
        out_exch=settings.RABBITMQ_ALEPH_EXCHANGE,
        out_key=settings.RABBITMQ_ALEPH_OUTPUT_KEY,
        react_fn=reactToAMQPMessage,
        glob=globals()                # used in deserializer
    )

    if "--foreground" in sys.argv:  # run at foreground
        daemon.run()
    else:
        daemon.run_daemon()         # run as daemon


#= Main program ===============================================================
if __name__ == '__main__':
    main()
