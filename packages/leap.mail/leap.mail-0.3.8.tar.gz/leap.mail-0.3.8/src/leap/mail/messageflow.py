# -*- coding: utf-8 -*-
# messageflow.py
# Copyright (C) 2013 LEAP
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
Message Producers and Consumers for flow control.
"""
import Queue

from twisted.internet.task import LoopingCall

from zope.interface import Interface, implements


class IMessageConsumer(Interface):

    def consume(self, item):
        """
        Consumes the passed item.

        :param item: an object to be consumed.
        :type item: object
        """
        # TODO we could add an optional type to be passed
        # for doing type check.

        # TODO in case of errors, we could return the object to
        # the queue, maybe wrapped in an object with a retries attribute.


class DummyMsgConsumer(object):

    implements(IMessageConsumer)

    def consume(self, item):
        """
        Just prints the passed item.
        """
        print "got item %s" % item


class MessageProducer(object):
    """
    A Producer class that we can use to temporarily buffer the production
    of messages so that different objects can consume them.

    This is useful for serializing the consumption of the messages stream
    in the case of an slow resource (db), or for returning early from a
    deferred chain and leave further processing detached from the calling loop,
    as in the case of smtp.
    """
    # TODO this can be seen as a first step towards properly implementing
    # components that implement IPushProducer / IConsumer  interfaces.
    # However, I need to think more about how to pause the streaming.
    # In any case, the differential rate between message production
    # and consumption is not likely (?) to consume huge amounts of memory in
    # our current settings, so the need to pause the stream is not urgent now.

    def __init__(self, consumer, queue=Queue.Queue, period=1):
        """
        Initializes the MessageProducer

        :param consumer: an instance of a IMessageConsumer that will consume
                         the new messages.
        :param queue: any queue implementation to be used as the temporary
                      buffer for new items. Default is a FIFO Queue.
        :param period: the period to check for new items, in seconds.
        """
        # XXX should assert it implements IConsumer / IMailConsumer
        # it should implement a `consume` method
        self._consumer = consumer

        self._queue = queue()
        self._period = period

        self._loop = LoopingCall(self._check_for_new)

    # private methods

    def _check_for_new(self):
        """
        Checks for new items in the internal queue, and calls the consume
        method in the consumer.

        If the queue is found empty, the loop is stopped. It will be started
        again after the addition of new items.
        """
        # XXX right now I'm assuming that the period is good enough to allow
        # a right pace of processing. but we could also pass the queue object
        # to the consumer and let it choose whether process a new item or not.

        if self._queue.empty():
            self.stop()
        else:
            self._consumer.consume(self._queue.get())

    # public methods

    def put(self, item):
        """
        Puts a new item in the queue.

        If the queue was empty, we will start the loop again.
        """
        was_empty = self._queue.empty()

        # XXX this might raise if the queue does not accept any new
        # items. what to do then?
        self._queue.put(item)
        if was_empty:
            self.start()

    def start(self):
        """
        Starts polling for new items.
        """
        if not self._loop.running:
            self._loop.start(self._period)

    def stop(self):
        """
        Stop polling for new items.
        """
        if self._loop.running:
            self._loop.stop()


if __name__ == "__main__":
    from twisted.internet import reactor
    producer = MessageProducer(DummyMsgConsumer())
    producer.start()

    for delay, item in ((2, 1), (3, 2), (4, 3),
                        (6, 4), (7, 5), (8, 6), (8.2, 7),
                        (15, 'a'), (16, 'b'), (17, 'c')):
        reactor.callLater(delay, producer.put, item)
    reactor.run()
