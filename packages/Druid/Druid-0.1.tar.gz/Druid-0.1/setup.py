# -*- coding: utf-8 -*-

# This file is part of Druid.
#
# Copyright (C) 2014 OKso (http://okso.me)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from setuptools import setup

with open('README.rst') as file:
    long_description = file.read()

setup(name='Druid',
      version='0.1',
      description='Doing Magic things with Tumulus',
      long_description=long_description,
      author='OKso.me',
      author_email='@okso.me',
      url='https://github.com/oksome/Druid',
      packages=['druid'],
      install_requires=['tumulus', 'Pillow'],
      license='AGPLv3',
      keywords="html generator template templating engine",
      classifiers=['Development Status :: 3 - Alpha',
                   'Environment :: Web Environment',
                   'Programming Language :: Python :: 3',
                   'Operating System :: POSIX',
                   'Operating System :: POSIX :: Linux',
                   'Operating System :: MacOS :: MacOS X',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: GNU Affero General Public License v3',
                   'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
                   'Topic :: Software Development :: Code Generators',
                   'Topic :: Software Development :: Libraries :: Python Modules',
                   'Topic :: Text Processing :: Markup :: HTML '
                   ],
      )
