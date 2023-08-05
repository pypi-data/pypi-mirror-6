#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2014 Vic Bukhantsov
#
# This file is part of ua2.table3
#
# ua2.table3 is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ua2.table3 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ua2.table3.  If not, see <http://www.gnu.org/licenses/>.
try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

import os

setup(
    name='ua2.table3',
    namespace_packages = ['ua2'],
    packages=find_packages('src'),
    package_data={'': ['*.*']},
    package_dir = {'': 'src'},
    entry_points = {},
    eager_resources = ['ua2'],
    version='0.2.1',
    install_requires=['Django>=1.5,<1.6'],
    license='BSD License',
    include_package_data=True,
    zip_safe=False,
    author='Viacheslav Vic Bukhantsov',
    author_email='vic@ua2web.com',
    platforms=['OS Independent'],

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Framework :: Django',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries'],
    description=('Alternative package for rendering tables'),
    long_description=open(os.path.join(os.path.dirname(__file__), 'README.rst')).read(),
    url='https://bitbucket.org/vic_in_kh/ua2.table3',
)
