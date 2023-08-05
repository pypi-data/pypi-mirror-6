# Copyright (c) 2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope.component import getMultiAdapter
from AccessControl import ModuleSecurityInfo, allow_module
from Products.Formulator.FieldRegistry import FieldRegistry

from silva.captcha import formulator
from silva.captcha.field import Captcha

FieldRegistry.registerField(formulator.CaptchaField) # XXX fix icon

allow_module('silva.captcha')
module_security = ModuleSecurityInfo('silva.captcha')
module_security.declareProtected('View', 'validate')
def validate(context, request, input):
    """Validate a potential captcha entry for a Python Script.
    """
    captcha = getMultiAdapter((context, request), name='captcha')
    return captcha.verify(input)
