# -*- coding: utf-8 -*-
# Copyright (c) 2010-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from zope.interface import implements
from zope.schema import ASCIILine
from zope.schema.interfaces import IASCIILine


class ICaptcha(IASCIILine):
    """A field for captcha validation
    """


class Captcha(ASCIILine):
    implements(ICaptcha)
