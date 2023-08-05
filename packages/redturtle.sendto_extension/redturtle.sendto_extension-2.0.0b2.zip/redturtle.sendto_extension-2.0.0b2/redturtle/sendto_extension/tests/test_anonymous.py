# -*- coding: utf-8 -*-

from Products.MailHost.interfaces import IMailHost
from pyquery import PyQuery
from zope.component import getMultiAdapter, getSiteManager
from collective.recaptcha.settings import getRecaptchaSettings
from plone.app.testing import TEST_USER_ID
from plone.app.testing import logout
from redturtle.sendto_extension.testing import SENDTOEXT_INTEGRATION_TESTING
from .base import BaseTestCase


class TestAnonymous(BaseTestCase):

    layer = SENDTOEXT_INTEGRATION_TESTING
    
    def setUp(self):
        BaseTestCase.setUp(self)
        self.settings = self.getSettings()
        self.recapcha_settings = getRecaptchaSettings()
        self.sm = getSiteManager(self.layer['portal'])
        self.view = getMultiAdapter((self.layer['portal'],
                                     self.layer['request']),
                                     name=u"sendto")
        logout()
    
    def test_basic_anon_access(self):
        portal = self.layer['portal']
        request = self.layer['request']
        self.settings.captcha = u''
        doc = PyQuery(self.view())
        self.assertEqual(doc('[name=send_from_address]').length, 1)
        self.assertEqual(doc('[name=send_to_address]').length, 1)
        self.assertEqual(doc('div.captcha').length, 0)

    def test_basic_anon_send(self):
        portal = self.layer['portal']
        request = self.layer['request']
        self.settings.captcha = u''
        request.form['form.submitted'] = '1'
        request.form['send_from_address'] = 'me@asdf.com'
        request.form['send_to_address'] = 'you@asdf.com'
        self.view()
        messages = self.sm.getUtility(IMailHost).sent
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0]['From'], 'webmaster@asdf.com')
        self.assertEqual(messages[0]['To'], 'you@asdf.com')

    def test_captcha_anon_access(self):
        portal = self.layer['portal']
        request = self.layer['request']
        self.recapcha_settings.public_key = 'foo'
        self.recapcha_settings.private_key = 'bar'
        self.settings.captcha = u'collective.recaptcha'
        doc = PyQuery(self.view())
        self.assertEqual(doc('[name=send_from_address]').length, 1)
        self.assertEqual(doc('[name=send_to_address]').length, 1)
        self.assertEqual(doc('div.captcha').length, 1)

