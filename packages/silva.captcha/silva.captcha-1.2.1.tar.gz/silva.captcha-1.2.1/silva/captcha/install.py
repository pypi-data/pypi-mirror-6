# Copyright (c) 2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$


from plone.keyring.interfaces import IKeyManager
from silva.core.upgrade.localsite import activate, disable
from zope.component import queryUtility

from utility import SilvaKeyManager


def install(context):
    """Install Captcha Support.
    """
    activate(context)
    sm = context.getSiteManager()
    sm.registerUtility(SilvaKeyManager(), IKeyManager)


def uninstall(context):
    """Uninstall Captcha Support.
    """
    disable(context, IKeyManager)


def is_installed(context):
    return not (queryUtility(IKeyManager) is None)



