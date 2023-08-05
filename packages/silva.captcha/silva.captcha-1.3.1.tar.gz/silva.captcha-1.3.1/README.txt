=========================
Captcha Support for Silva
=========================

This is a captcha support for Silva. It works with the help of
``skimpyGimpy``.

After installing the extension, you can either use a ``zeam.form``
widget, a Formulator widget or ask the captcha directly.

You can get the captcha image in your template the following way::

   <tal:captcha tal:define="captcha nocall:here/@@captcha"
                tal:content="structure captcha/image_tag">
   </tal:captcha>

You can get the captcha as a sound file like this::

   <div class="captchaAudio"
        tal:define="captcha nocall:here/@@captcha">
      <a href="#" target="_blank"
         tal:attributes="href captcha/audio_url">Audio version</a>
   </div>

You can validate an captcha entry in Python like this::

   from zope.component import getMultiAdapter


   captcha = getMultiAdapter((self.context, self.request), name='captcha')
   if not captcha.verify(input):
       # Bad value
   else:
       # Good value

This extension require at least `Silva`_ 2.3 or higher. For previous
version of Silva, you can use previous versions of the extension.

Use in Python Script
--------------------

In your Python Script/Code Sources, you can use for example::

  from silva.captcha import validate

  request = context.REQUEST
  input = request.form.get('captcha_field', None)
  if not validate(context, request, input):
      # Bad value
  else:
      # Good value


This will validate (or not) the input of the captcha.


Code repository
---------------

You can find the code of this extension in Git:
https://github.com/silvacms/silva.captcha.


.. _Silva: http://silvacms.org
