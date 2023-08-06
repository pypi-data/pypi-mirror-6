# -*- coding: utf-8 -*-
##############################################################################
#
#  Agha, Another GitHub API
#  Copyright (C) 2014 MRDEV Software (<http://mrdev.com.ar>).
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

__version__ = '0.1.0'
__license__ = 'LGPL-3'

from setuptools import setup

setup(
    name = 'agha',
    version=__version__,
    url='http://github.com/mrsarm/python-agha',
    download_url = 'https://github.com/mrsarm/python-agha/tarball/' + __version__,
    license=__license__,
    author='Mariano Ruiz',
    author_email='mrsarm@gmail.com',
    description='Agha, Another GitHub API',
    packages=[
        'agha',
    ],
    zip_safe=False,
    platforms='any',
    install_requires=[
        'requests>=2.2',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)
