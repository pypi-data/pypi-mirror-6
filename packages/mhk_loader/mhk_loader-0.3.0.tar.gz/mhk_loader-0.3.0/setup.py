# -*- coding: utf-8 -*-
# Copyright (c) 2013,2014 Rodolphe Quiédeville <rodolphe@quiedeville.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from setuptools import setup
import os
from mhk_loader import __version__

VERSION = __version__

setup(
    name="mhk_loader",
    version=VERSION,
    description="Read tsung logs and push datas to Maheki",
    long_description="""Maheki loader is usefull to upload datas
    extract from tsung log files (required loglevel=notice) and upload
    them to a maheki server installed on other server.

* Maheki: https://gitorious.org/maheki
* Tsung : http://tsung.erlang-projects.org/

""",
    scripts=['mhk_loader.py'],
    author="Rodolphe Quiédeville",
    author_email="rodolphe@quiedeville.org",
    url="https://github.com/rodo/mhk_loader",
    requires=['requests',],
    install_requires=['requests',],
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python',
        'Operating System :: OS Independent',
        'Topic :: System :: Monitoring',
        ],
    include_package_data=True,
    )
