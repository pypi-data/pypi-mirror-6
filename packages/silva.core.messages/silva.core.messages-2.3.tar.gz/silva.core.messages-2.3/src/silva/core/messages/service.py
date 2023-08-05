# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt

from five import grok
from silva.core.messages.interfaces import IMessageService, IMessage
from silva.core.cache.store import SessionStore


class Message(object):
    grok.implements(IMessage)

    namespace = None

    def __init__(self, string, namespace='message'):
        self.content = string
        self.namespace = namespace

    def __str__(self):
        return self.content

    def __unicode__(self):
        return self.content


STORE_KEY = 'messages'


class MessageService(grok.GlobalUtility):
    grok.provides(IMessageService)
    grok.implements(IMessageService)


    def __retrieve(self, request):
        store = SessionStore(request)
        messages = store.get(STORE_KEY, list())
        return (store, messages)

    def send(self, message_str, request, namespace=u"message"):
        store, messages = self.__retrieve(request)
        messages.append(Message(message_str, namespace=namespace))
        store.set(STORE_KEY, messages)

    def receive(self, request, namespace=u"message"):
        store, messages = self.__retrieve(request)
        keep = list()
        reception = list()
        for message in messages:
            if message.namespace != namespace:
                keep.append(message)
            else:
                reception.append(message)
        store.set(STORE_KEY, keep)
        return reception

    def receive_all(self, request):
        store, messages = self.__retrieve(request)
        store.set(STORE_KEY, list())
        return messages
