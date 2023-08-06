Django Staticsfiles Ignore Debug
================================

Serve static files below a given point in the directory structure or
from locations inferred from the staticfiles finders in *Django* projects.

To use, put a URL pattern such as:

.. code:: python

    (r'^%s(?P<path>.*)$' % re.escape(settings.STATIC_URL.lstrip('/')), \
            'staticsfiles_ignoredebug.views.serve')

in your URLconf.

It uses the ``django.views.static`` view to serve the found files.

At difference from ``django.contrib.staticfiles.urls.staticfiles_urlpatterns``
(https://docs.djangoproject.com/en/1.4/ref/contrib/staticfiles/#django.contrib.staticfiles.templatetags.staticfiles.django.contrib.staticfiles.urls.staticfiles_urlpatterns),
this function allow serve the static content in non *DEBUG* mode.

If ``DEBUG=False`` and ``STATICFILES_IGNORE_DEBUG=False`` a ``ImproperlyConfigured``
exception is raised.

**DISCLAIMER**: Using this method is inefficient and insecure.
Do not use this in a production setting. Use this only for development and
testing environment with ``DEBUG=False``.

About
-----

The project **staticsfiles_ignoredebug** was developed
by **Mariano Ruiz** on **Enterprise Objects Consulting**.

This sources are available in https://github.com/eoconsulting/django-staticsfiles-ignoredebug

License: LGPL-3 (C) 2013
