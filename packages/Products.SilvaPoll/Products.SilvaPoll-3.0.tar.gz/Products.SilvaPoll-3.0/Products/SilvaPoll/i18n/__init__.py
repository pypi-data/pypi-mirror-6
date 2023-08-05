# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013 Infrae. All rights reserved.
# See also LICENSE.txt
"""Provides a function called 'translate' that *must* be imported as '_':

    from Products.SilvaPoll.i18n import translate as _

and will provide a MessageFactory that returns Messages for
i18n'ing Product code and Python scripts.
"""
from zope.i18nmessageid import MessageFactory

translate = MessageFactory('silva_poll')
