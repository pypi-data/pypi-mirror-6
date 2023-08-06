# -*- coding: utf-8 -*-
##############################################################################
#
#    Django Common Context Processors
#    Copyright (C) 2014 Mariano Ruiz <mrsarm@gmail.com>
#    All Rights Reserved
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

__version__ = '0.1.0'
__license__ = 'LGPL-3'

from setuptools import setup

setup(
    name = 'django_common_context',
    version=__version__,
    url='http://github.com/mrsarm/django-common-context',
    download_url = 'https://github.com/mrsarm/django-common-context/tarball/' + __version__,
    license=__license__,
    author='Mariano Ruiz',
    author_email='mrsarm@gmail.com',
    description='Django Common Context Processors',
    packages=[
        'common_context',
        'common_context.context_processors',
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
