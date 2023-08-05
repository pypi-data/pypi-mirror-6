# -*- coding: utf-8 -*-

from zope.configuration import xmlconfig

from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting
from plone.app.testing import applyProfile
from plone.app.testing import setRoles
from plone.app.testing import applyProfile
from plone.app.testing import TEST_USER_ID


class SendToExtentionLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        # Load ZCML for this package
        import redturtle.sendto_extension
        import collective.recaptcha
        xmlconfig.file('configure.zcml',
                       redturtle.sendto_extension,
                       context=configurationContext)
        xmlconfig.file('configure.zcml',
                       collective.recaptcha,
                       context=configurationContext)


    def setUpPloneSite(self, portal):
        applyProfile(portal, 'redturtle.sendto_extension:default')
        setRoles(portal, TEST_USER_ID, ['Member', 'Manager'])


SENDTOEXT_FIXTURE = SendToExtentionLayer()
SENDTOEXT_INTEGRATION_TESTING = \
    IntegrationTesting(bases=(SENDTOEXT_FIXTURE, ),
                       name="SendToExtentionIntegration")
SENDTOEXT_FUNCTIONAL_TESTING = \
    FunctionalTesting(bases=(SENDTOEXT_FIXTURE, ),
                      name="SendToExtention:Functional")

