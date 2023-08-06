# -*- coding: utf-8 -*-
##############################################################################
#
#  Django Staticfiles Ignore Debug
#  Copyright (C) 2013  Enterprise Objects Consulting
#  All Rights Reserved
#
#  Author: Mariano Ruiz <mrsarm@gmail.com>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with this programe.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


import os
import posixpath
import urllib
from django.http import Http404
from django.views import static
from django.contrib.staticfiles import finders
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings


def serve(request, path, document_root=None, insecure=False, **kwargs):
    """
    Serve static files below a given point in the directory structure or
    from locations inferred from the staticfiles finders.

    To use, put a URL pattern such as::

        (r'^%s(?P<path>.*)$' % re.escape(settings.STATIC_URL.lstrip('/')), 'staticsfiles_ignoredebug.views.serve')

    in your URLconf.

    It uses the django.views.static view to serve the found files.

    At difference from django.contrib.staticfiles.urls.staticfiles_urlpatterns
    (https://docs.djangoproject.com/en/1.4/ref/contrib/staticfiles/#django.contrib.staticfiles.templatetags.staticfiles.django.contrib.staticfiles.urls.staticfiles_urlpatterns),
    this function allow serve the static content in non DEBUG mode.

    If DEBUG=False and STATICFILES_IGNORE_DEBUG=False a ImproperlyConfigured
    exception is raised.

    DISCLAIMER: Using this method is inefficient and insecure.
    Do not use this in a production setting. Use this only for development and
    testing environment with DEBUG=False.
    """
    try:
        if not settings.DEBUG and not insecure \
                and not settings.STATICFILES_IGNORE_DEBUG:
            raise ImproperlyConfigured("The staticfiles view can only be used in "
                                       "debug mode or if the the --insecure "
                                       "option of 'runserver' is used, "
                                       "or STATICFILES_IGNORE_DEBUG=True")
    except AttributeError:
        pass
    normalized_path = posixpath.normpath(urllib.unquote(path)).lstrip('/')
    absolute_path = finders.find(normalized_path)
    if not absolute_path:
        if path.endswith('/') or path == '':
            raise Http404("Directory indexes are not allowed here.")
        raise Http404("'%s' could not be found" % path)
    document_root, path = os.path.split(absolute_path)
    return static.serve(request, path, document_root=document_root, **kwargs)
