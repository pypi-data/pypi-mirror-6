# Copyright (c) 2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$


import unittest

from Products.Silva.testing import SilvaLayer
from Products.Formulator import Form
from zope.component import queryMultiAdapter
import silva.captcha


FunctionalLayer = SilvaLayer(silva.captcha)


class FormulatorFieldTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        """After set up, install the extension.
        """
        self.root = self.layer.get_application()
        self.layer.login('manager')

    def test_functional(self):
        root = self.root
        captcha = queryMultiAdapter((root, root.REQUEST), name='captcha')
        captcha._generate_session()
        root.REQUEST['silva_captcha'] = root.REQUEST.response.cookies[
            'silva_captcha']['value']

        factory = root.manage_addProduct['Formulator']
        factory.manage_add('form', 'Test form')
        factory = root.form.manage_addProduct['Formulator']
        factory.manage_addField('captcha_field', 'Test Captcha', 'CaptchaField')

        self.assertEqual(len(root.form.get_fields()), 1)

        # I don't think it ever generates 'foo', but still...
        words = captcha._generate_words()
        invalid_word = 'foo'
        while invalid_word in words:
            invalid_word += 'o'

        self.assertRaises(
            Form.FormValidationError,
            root.form.validate_all, {'field_captcha_field': invalid_word})

        self.assertEqual(
            root.form.validate_all({'field_captcha_field': words[0]}),
            {'captcha_field': True})


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(FormulatorFieldTestCase))
    return suite
