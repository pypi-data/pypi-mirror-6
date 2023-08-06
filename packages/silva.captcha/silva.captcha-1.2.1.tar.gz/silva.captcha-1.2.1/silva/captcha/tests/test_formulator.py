# Copyright (c) 2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from Products.Five import zcml

from Products.Silva.tests import SilvaTestCase

from Testing.ZopeTestCase.layer import onsetup as ZopeLiteLayerSetup
from Testing.ZopeTestCase import installPackage, installProduct

from zope.component import queryMultiAdapter

from silva.captcha import formulator
from Products.Formulator import Form
from Products.Formulator import Errors

class Container(dict):
    """ dict with getattr access to items
    """
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError, e:
            raise AttributeError(e)

class FormulatorFieldTestCase(SilvaTestCase.SilvaTestCase):

    def afterSetUp(self):
        """After set up, install the extension.
        """
        root = self.getRoot()
        root.service_extensions.install('silva.captcha')

    def test_functional(self):
        root = self.getRoot()
        captcha = queryMultiAdapter((root, root.REQUEST), name='captcha')
        captcha._generate_session()
        root.REQUEST['captchasessionid'] = root.REQUEST.response.cookies[
            'captchasessionid']['value']

        root.manage_addProduct['Formulator'].manage_add('form', 'Test form')
        form = root.form
        form.manage_addProduct['Formulator'].manage_addField(
            'captcha_field', 'Test Captcha Field', 'CaptchaField')

        # i don't think it ever generates 'foo', but still...
        words = captcha._generate_words()
        teststr = 'foo'
        while teststr in words:
            teststr += 'o'
        self.assertRaises(
            Form.FormValidationError, form.validate_all,
            {'field_captcha_field': teststr})

        form.validate_all({'field_captcha_field': words[0]})


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
    suite.addTest(unittest.makeSuite(FormulatorFieldTestCase))
    return suite
