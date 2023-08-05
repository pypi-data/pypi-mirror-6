# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt

import unittest

from Products.Silva.testing import FunctionalLayer
from zope.component import getUtility
from zope.interface.verify import verifyObject
from zope.publisher.browser import TestRequest

from silva.core.messages.interfaces import IMessageService


def messages_to_string(messages):
    return [(message.namespace, str(message),) for message in messages]


class UtilityTest(unittest.TestCase):
    # XXX I don't think this test needs FunctionalLayer
    layer = FunctionalLayer

    def setUp(self):
        self.request = TestRequest()

    def test_utility(self):
        service = getUtility(IMessageService)
        self.assertTrue(verifyObject(IMessageService, service))

        service.send(u"some unicode message", self.request)
        self.assertEquals(
            [(u'message', u"some unicode message",)],
            messages_to_string(service.receive_all(self.request)))


class MessagingTest(unittest.TestCase):

    layer = FunctionalLayer

    def setUp(self):
        self.request = TestRequest()
        self.service = getUtility(IMessageService)

    def test_no_messages(self):
        self.assertEquals([], self.service.receive(self.request))

    def test_multiple_messages(self):
        self.service.send(u'message1', self.request)
        self.service.send(u'message2', self.request)
        self.assertEquals(
            [(u'message', u'message1',),
             (u'message', u'message2',)],
            messages_to_string(self.service.receive_all(self.request)))
        self.assertEquals([], self.service.receive_all(self.request))

    def test_multiple_messages_of_different_type(self):
        self.service.send(u'message_type1', self.request, namespace=u"type1")
        self.service.send(u'message_type2', self.request, namespace=u"type2")
        self.service.send(u'message_type1', self.request, namespace=u"type1")

        def receive(type):
            return self.service.receive(self.request, type)

        self.assertEquals(
            [u'message_type1',
             u'message_type1',],
            map(str, receive(u'type1')))
        self.assertEquals([], receive(u'type1'))

        self.assertEquals(
            [u'message_type2',], map(str, receive(u'type2')))
        self.assertEquals([], receive(u'type2'))

    def test_multiple_messages_of_different_type_fetch_all_at_once(self):
        self.service.send(u'message_type1', self.request, namespace=u"type1")
        self.service.send(u'message_type2', self.request, namespace=u"type2")
        self.service.send(u'message_type1', self.request, namespace=u"type1")

        self.assertEquals(
            [(u'type1', u'message_type1',),
             (u'type2', u'message_type2',),
             (u'type1', u'message_type1',)],
            messages_to_string(self.service.receive_all(self.request)))
        self.assertEquals([], self.service.receive_all(self.request))


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(UtilityTest))
    suite.addTest(unittest.makeSuite(MessagingTest))
    return suite
