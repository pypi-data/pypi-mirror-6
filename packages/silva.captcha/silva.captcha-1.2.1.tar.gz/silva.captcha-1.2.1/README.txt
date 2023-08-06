Copyright (c) 2008-2009, Infrae. All rights reserved.
See also LICENSE.txt

Captcha Support for Silva
-------------------------

This is a captcha support for Silva. It works with the help of
``collective.captcha``, and ``plone.keyring``.

After installing the extension, you can either use a formlib widget,
or ask the captcha directly.

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

You can validate an captcha entry like this::

   from zope.component import getMultiAdapter


   captcha = getMultiAdapter((self.context, self.request), name='captcha')
   if not captcha.verify(input):
       # Bad value
   else:
       # Good value

This extension require at least `Silva`_ 2.0.7 or higher. You can have
more information about `collective.captcha`_.

Use in Python Script
~~~~~~~~~~~~~~~~~~~~

In your Python Script/Code Sources, you can use for example::

  from silva.captcha import validate

  request = context.REQUEST
  input = request.form.get('captcha_field', None)
  if not validate(context, request, input):
      # Bad value
  else:
      # Good value


This will validate (or not) the input of the captcha.


Installation
------------

If you installed Silva using buildout, by getting one from the `Infrae
SVN`_ repository, or creating one using `Paster`_, you should edit your
buildout configuration file ``buildout.cfg`` to add or edit the
following section::

  [instance]

  eggs = ...
        silva.captcha

  zcml = ...
        silva.captcha

If the section ``instance`` wasn't already in the configuration file,
pay attention to re-copy values for ``eggs`` and ``zcml`` from the
profile you use.

After you can restart buildout::

  $ ./bin/buildout


If you don't use buildout, you can install this extension using
``easy_install``, and after create a file called
``silva.captcha-configure.zcml`` in the
``/path/to/instance/etc/package-includes`` directory.  This file will
responsible to load the extension and should only contain this::

  <include package="silva.captcha" />


Latest version
--------------

The latest version is available in a `Subversion repository
<https://svn.infrae.com/silva.captcha/trunk#egg=silva.captcha-dev>`_.


.. _Infrae SVN: https://svn.infrae.com/buildout/silva/
.. _Paster: https://svn.infrae.com/buildout/silva/INSTALL.txt
.. _Silva: http://infrae.com/products/silva
.. _collective.captcha: http://pypi.python.org/pypi/collective.captcha
