# -*- coding: utf-8 -*-

from zope.interface import implements
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.component.hooks import getSite

from redturtle.sendto_extension import _
from redturtle.sendto_extension import logger

class CaptchaVocabulary(object):
    """Vocabulary for the captcha selection in control panel
    """
    implements(IVocabularyFactory)

    def __call__(self, context):
        portal = getSite()
        
        # have repactha?
        recaptcha = portal.restrictedTraverse('@@captcha/image_tag', None)
        
        terms = [SimpleTerm(u'', _(u'No protection! Risky Bussiness!')), ]
        if recaptcha:
            try:
                recaptcha()
                terms.append(SimpleTerm(u'collective.recaptcha', _(u'Recaptcha protection')),)
            except ValueError, inst:
                logger.warning("Can't use recaptcha protection. It seems not configured:\n%s" % inst)
        return SimpleVocabulary(terms)

captchaVocabularyFactory = CaptchaVocabulary()