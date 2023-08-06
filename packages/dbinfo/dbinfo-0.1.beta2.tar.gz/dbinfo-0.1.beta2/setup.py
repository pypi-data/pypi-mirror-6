# -*- coding: utf-8 -*-
##############################################################################
#
#  DB Info, Database Information Tool
#  Copyright (C) 2013 MRDEV Software (<http://mrdev.com.ar>).
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
import dbinfo
from dbinfo.dbinfo import __version__, __license__

setup(
    name = 'dbinfo',
    version=__version__,
    license=__license__,
    url='https://launchpad.net/dbinfo',
    download_url='https://launchpad.net/dbinfo/trunk/%s/+download/dbinfo-%s.tar.gz' % (__version__, __version__),
    author='Mariano Ruiz',
    author_email='mrsarm@gmail.com',
    description='Database Information Tool',
    packages=[
        'dbinfo',
    ],
    zip_safe=False,
    platforms='any',
    install_requires=[
        'psycopg2',
        'MySQL-python',
    ],
    entry_points = {
        'console_scripts': [
            'dbinfo-pg = dbinfo.dbinfo:main_pg',
            'dbinfo-my = dbinfo.dbinfo:main_my',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Customer Service',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)', 
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Database',
    ],
)
