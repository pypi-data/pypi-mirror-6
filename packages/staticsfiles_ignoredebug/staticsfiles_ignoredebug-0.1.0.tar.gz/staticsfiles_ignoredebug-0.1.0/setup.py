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


from setuptools import setup
import staticsfiles_ignoredebug

setup(
    name = 'staticsfiles_ignoredebug',
    version=staticsfiles_ignoredebug.__version__,
    url='http://github.com/eoconsulting/django-staticsfiles-ignoredebug',
    download_url = 'https://github.com/eoconsulting/django-staticsfiles-ignoredebug/tarball/' + staticsfiles_ignoredebug.__version__,
    license=staticsfiles_ignoredebug.__license__,
    author=staticsfiles_ignoredebug.__author__,
    author_email='mrsarm@gmail.com',
    description='Django Staticsfiles Ignore Debug',
    packages=[
        'staticsfiles_ignoredebug',
        'staticsfiles_ignoredebug.views',
    ],
    zip_safe=False,
    platforms='any',
    install_requires=[
        'Django>=1.4',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
