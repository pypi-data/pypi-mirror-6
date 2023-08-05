# -*- coding: utf-8 -*-

import unittest
from email import message_from_string

from zope import interface
from zope.component import queryUtility, getSiteManager

from Products.MailHost.interfaces import IMailHost
from Products.MailHost.MailHost import MailHost
from plone.registry.interfaces import IRegistry

from redturtle.sendto_extension.interfaces import IRTSendToExtensionLayer, ISendtoExtensionSettings


class DummyMailHost(MailHost):
    # Stolen from plone.app.contentrules tests
    meta_type = 'Dummy Mail Host'

    def __init__(self, id):
        self.id = id
        self.sent = []

    def _send(self, mfrom, mto, messageText, *args, **kw):
        msg = message_from_string(messageText)
        self.sent.append(msg)



class BaseTestCase(unittest.TestCase):
    
    def registerMailHost(self):
        sm = getSiteManager(self.layer['portal'])
        sm.unregisterUtility(provided=IMailHost)
        dummyMailHost = DummyMailHost('dMailhost')
        sm.registerUtility(dummyMailHost, IMailHost)
    
    def getSettings(self):
        registry = queryUtility(IRegistry)
        return registry.forInterface(ISendtoExtensionSettings, check=False)

    def markRequestWithLayer(self):
        # to be removed when p.a.testing will fix https://dev.plone.org/ticket/11673
        request = self.layer['request']
        interface.alsoProvides(request, IRTSendToExtensionLayer)

    def setUp(self):
        self.markRequestWithLayer()
        self.registerMailHost()
        portal = self.layer['portal']
        portal.manage_changeProperties(email_from_address='webmaster@asdf.com')
