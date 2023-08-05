# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from Products.Formulator import Validator
from Products.Formulator import Widget
from Products.Formulator import Field
from Products.Formulator.i18n import translate as _
from zope.component import queryMultiAdapter


class CaptchaValidator(Validator.Validator):
    """ validate the captcha
    """
    message_names = Validator.Validator.message_names + [
        'required_not_found', 'captcha_invalid']
    required_not_found = _('Input is required but no input given.')
    captcha_invalid = _('The verification entry is not valid.')

    def validate(self, field, key, REQUEST):
        value = REQUEST.get(key, '')
        if value == '':
            self.raise_error('required_not_found', field)

        captcha = queryMultiAdapter((field, field.REQUEST), name='captcha')
        if not captcha.verify(value):
            self.raise_error('captcha_invalid', field)
        return True # we don't need to return the value, it doesn't matter


CaptchaValidatorInstance = CaptchaValidator()


class CaptchaWidget(Widget.Widget):
    """ the widget for the captcha

        renders the image and an input field
    """
    property_names = ['title', 'description', 'css_class', 'alternate_name']

    def render(self, field, key, value, REQUEST):
        """ render the widget
        """
        captcha = queryMultiAdapter((field, field.REQUEST), name='captcha')
        image = captcha.image_tag()
        input = Widget.render_element(
            "input", type="text", name=key,
            css_class=field.get_value('css_class'),
            value=value)
        return (
            '<div class="form-captcha">' +
            '<div class="form-captcha-img">' + image + '</div>' +
            '<div class="form-captcha-input">' + input + '</div>' +
            '</div>')

    def render_view(self, field, value):
        return ''


CaptchaWidgetInstance = CaptchaWidget()


class CaptchaField(Field.ZMIField):
    meta_type = 'CaptchaField'
    widget = CaptchaWidgetInstance
    validator = CaptchaValidatorInstance

    def _get_default(self, key, value, REQUEST):
        return ''

    def get_value(self, id, **kw):
        if id == 'hidden':
            return False
        return super(CaptchaField, self).get_value(id, **kw)
