#
#  Copyright 2014 Johannes Spielmann <jps@shezi.de>
#
#  This file is part of django-micro-cms.
#
#  django-micro-cms is free software: you can redistribute it and/or
#  modify it under the terms of the GNU General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#
#  django-micro-cms is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with django-micro-cms.  If not, see <http://www.gnu.org/licenses/>.

from distutils.core import setup

with open('README.rst') as file:
    long_description = file.read()

import microcms
    
setup(
    name='django-micro-cms',
    version=microcms.__version__,
    
    packages=['microcms' ],
    
    url='https://bitbucket.org/shezi/django-micro-cms/',
    
    author='Johannes Spielmann',
    author_email='jps@shezi.de',
    
    description='A micro-CMS for django. A bit like flatpages++.',
    long_description=long_description,
    
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        ],
    )
