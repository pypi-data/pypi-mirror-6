#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
#= Imports ====================================================================
"""
Script which simplifies debugging and testing AMQP communication, routing, keys
and so on.
"""
import sys
import uuid
import argparse


import pika


import aleph
import amqpdaemon

from settings import *


try:
    from edeposit.amqp.serializers import serializers
except ImportError:
    from serializers import serializers


def createBlockingConnection():
    """
    Return properly created blocking connection.

    Uses :func:`edeposit.amqp.amqpdaemon.getConParams`.
    """
    return pika.BlockingConnection(
        amqpdaemon.getConParams(RABBITMQ_ALEPH_VIRTUALHOST)
    )


def receive(queue):
    """
    Print all messages from :attr:`edeposit.amqp.settings`
    ``RABBITMQ_ALEPH_OUTPUT_QUEUE``.
    """
    for method_frame, properties, body in channel.consume(queue):
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

    Note:
        This is here mainly for testing purposes. Proper schema will require
        more routing keys.
    """
    exchanges = [
        "search",
        "count",
        "export",
        "validate"
    ]
    queues = {
        RABBITMQ_ALEPH_OUTPUT_QUEUE: RABBITMQ_ALEPH_OUTPUT_KEY,
        RABBITMQ_ALEPH_INPUT_QUEUE: RABBITMQ_ALEPH_INPUT_KEY
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

    print "\tRouting exchange search['%s'] -> '%s'." % (RABBITMQ_ALEPH_EXCEPTION_KEY, RABBITMQ_ALEPH_OUTPUT_QUEUE)
    channel.queue_bind(
        queue=RABBITMQ_ALEPH_OUTPUT_QUEUE,
        exchange="search",
        routing_key=RABBITMQ_ALEPH_EXCEPTION_KEY
    )


#= Main program ===============================================================
if __name__ == '__main__':
    # parse arguments
    parser = argparse.ArgumentParser(description="AMQP debugger.")
    parser.add_argument(
        '--put',
        action='store_true',
        help="Put one message into queue %s." % (RABBITMQ_ALEPH_INPUT_QUEUE)
    )
    parser.add_argument(
        '--put-bad',
        action='store_true',
        help="Put error message into queue %s." % (RABBITMQ_ALEPH_INPUT_QUEUE)
    )
    parser.add_argument(
        '--get',
        action='store_true',
        help="Get one message from queue %s." % (RABBITMQ_ALEPH_INPUT_QUEUE)
    )
    parser.add_argument(
        '--create',
        action='store_true',
        help="Create the schema in RabbitMQ."
    )
    parser.add_argument(
        '--timeout',
        metavar="N",
        type=int,
        default=-1,
        help="Wait for message only N seconds."
    )
    args = parser.parse_args()

    # variable initialization
    isbnq = aleph.ISBNQuery("80-251-0225-4")
    request = aleph.SearchRequest(isbnq)
    json_data = serializers.serialize(request)

    connection = createBlockingConnection()

    # register timeout
    if args.timeout > 0:
        connection.add_timeout(
            args.timeout,
            lambda: sys.stderr.write("Timeouted\n") or sys.exit(1)
        )

    channel = connection.channel()

    properties = pika.BasicProperties(
        content_type="application/json",
        delivery_mode=1,
        headers={"UUID": str(uuid.uuid4())}
    )

    # react to parameters
    if args.create:
        createSchema()

    if args.put:
        channel.basic_publish(
            exchange=RABBITMQ_ALEPH_EXCHANGE,
            routing_key=RABBITMQ_ALEPH_INPUT_KEY,
            properties=properties,
            body=json_data
        )

    if args.put_bad:
        channel.basic_publish(
            exchange=RABBITMQ_ALEPH_EXCHANGE,
            routing_key=RABBITMQ_ALEPH_INPUT_KEY,
            properties=properties,
            body="xex"
        )

    if args.get:
        try:
            receive(RABBITMQ_ALEPH_OUTPUT_QUEUE)
        except KeyboardInterrupt:
            print
            sys.exit(0)
