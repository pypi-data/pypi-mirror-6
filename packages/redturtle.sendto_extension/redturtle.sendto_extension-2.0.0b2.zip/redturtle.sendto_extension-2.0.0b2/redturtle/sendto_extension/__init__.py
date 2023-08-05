# -*- coding: utf-8 -*-

import logging

from zope.i18nmessageid import MessageFactory

_ = MessageFactory('redturtle.sendto_extension')
logger = logging.getLogger('redturtle.sendto_extension')


def initialize(context):
    """Initializer called when used as a Zope 2 product."""
