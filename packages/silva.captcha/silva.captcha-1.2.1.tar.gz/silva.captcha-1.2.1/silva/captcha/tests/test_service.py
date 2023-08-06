# Copyright (c) 2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope.component import queryMultiAdapter
from silva.captcha import validate

from Products.Five import zcml

from Products.Silva.tests import SilvaTestCase
from Testing.ZopeTestCase.layer import onsetup as ZopeLiteLayerSetup
from Testing.ZopeTestCase import installProduct, installPackage


class CaptchaTestCase(SilvaTestCase.SilvaTestCase):
    """Test case for captcha integration.
    """

    def afterSetUp(self):
        """After set up, install the extension.
        """
        root = self.getRoot()
        root.service_extensions.install('silva.captcha')

    def test_00install(self):
        """Install should change the members services and set up an
        acl_user.
        """
        root = self.getRoot()

        # First the extension should be installed
        service_extensions = root.service_extensions
        self.failUnless(service_extensions.is_installed('silva.captcha'))

        # And should get a captcha
        captcha = queryMultiAdapter((root, root.REQUEST), name='captcha')
        self.failIf(captcha is None)
        # Invalid entry
        self.failIf(captcha.verify(None))
        self.failIf(validate(root, root.REQUEST, None))

    def test_20uninstall(self):
        """Uninstall should work.
        """
        root = self.getRoot()
        root.service_extensions.uninstall('silva.captcha')
        self.failIf(root.service_extensions.is_installed('silva.captcha'))


@ZopeLiteLayerSetup
def installCaptcha():
    installPackage('silva.captcha')

    # Load our ZCML, which add the extension as a Product
    from silva import captcha
    zcml.load_config('configure.zcml', captcha)


import unittest
def test_suite():

    # Install GenericSetup if it's there.
    try:
        import Products.GenericSetup
        installProduct('GenericSetup')
    except ImportError:
        pass
    installCaptcha()

    # Run tests
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(CaptchaTestCase))
    return suite
