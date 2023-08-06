# -*- coding: utf-8 -*-

import logging

from zope.i18nmessageid import MessageFactory

_ = MessageFactory('collective.typecriterion')
logger = logging.getLogger('collective.typecriterion')

def initialize(context):
    """Initializer called when used as a Zope 2 product."""
