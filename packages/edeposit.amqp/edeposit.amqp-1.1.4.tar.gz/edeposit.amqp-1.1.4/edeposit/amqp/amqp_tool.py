#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
#= Imports ====================================================================
import sys
import uuid


import pika


import aleph
import aleph.convertors
import alephdaemon

from settings import *


def createBlockingConnection():
    """
    Return properly created blocking connection.

    Uses .getConnectionParameters() from alephdaemon.py.
    """
    return pika.BlockingConnection(alephdaemon.getConnectionParameters())


def receive():
    """
    Print all received messages.
    """
    for method_frame, properties, body in channel.consume(RABBITMQ_ALEPH_PLONE_QUEUE):
        print "Message:"
        print method_frame
        print properties
        print body
        print "---"
        print

        channel.basic_ack(method_frame.delivery_tag)


def createSchema():
    """
    Create the routing schema in rabbitmq's database.
    """
    exchanges = [
        "search",
        "count",
        "export"
    ]
    queues = {
        RABBITMQ_ALEPH_PLONE_QUEUE: RABBITMQ_ALEPH_PLONE_KEY,
        RABBITMQ_ALEPH_DAEMON_QUEUE: RABBITMQ_ALEPH_DAEMON_KEY
    }

    connection = createBlockingConnection()
    channel = connection.channel()

    print "Creating exchanges:"
    for exchange in exchanges:
        channel.exchange_declare(
            exchange=exchange,
            exchange_type="topic",
            durable=True
        )
        print "\tCreated exchange '%s' of type 'topic'." % (exchange)

    print
    print "Creating queues:"
    for queue in queues.keys():
        channel.queue_declare(
            queue=queue,
            durable=True,
            # arguments={'x-message-ttl': int(1000 * 60 * 60 * 24)} # :S
        )
        print "\tCreated durable queue '%s'." % (queue)

    print
    print "Routing exchanges using routing key to queues:"
    for exchange in exchanges:
        for queue in queues.keys():
            channel.queue_bind(
                queue=queue,
                exchange=exchange,
                routing_key=queues[queue]
            )
            print "\tRouting exchange %s['%s'] -> '%s'." % (exchange, queues[queue], queue)

    print "\tRouting exchange search['%s'] -> '%s'." % (RABBITMQ_ALEPH_EXCEPTION_KEY, RABBITMQ_ALEPH_PLONE_QUEUE)
    channel.queue_bind(
        queue=RABBITMQ_ALEPH_PLONE_QUEUE,
        exchange="search",
        routing_key=RABBITMQ_ALEPH_EXCEPTION_KEY
    )


#= Main program ===============================================================
if __name__ == '__main__':
    isbnq = aleph.ISBNQuery("80-251-0225-4")
    request = aleph.SearchRequest(isbnq)
    json_data = aleph.convertors.toJSON(request)

    connection = createBlockingConnection()
    channel = connection.channel()

    properties = pika.BasicProperties(
        content_type="application/json",
        delivery_mode=1,
        headers={"UUID": str(uuid.uuid4())}
    )

    if "--create" in sys.argv:
        createSchema()

    if "--put" in sys.argv:
        channel.basic_publish(
            exchange=RABBITMQ_ALEPH_EXCHANGE,
            routing_key=RABBITMQ_ALEPH_DAEMON_KEY,
            properties=properties,
            body=json_data
        )

    if "--put-bad" in sys.argv:
        channel.basic_publish(
            exchange=RABBITMQ_ALEPH_EXCHANGE,
            routing_key=RABBITMQ_ALEPH_DAEMON_KEY,
            properties=properties,
            body="xex"
        )

    if "--get" in sys.argv:
        try:
            receive()
        except KeyboardInterrupt:
            print
            sys.exit(0)

    if len(sys.argv) == 1:
        print "Usage " + sys.argv[0] + " [--get] [--put] [--put-bad] [--create]"
