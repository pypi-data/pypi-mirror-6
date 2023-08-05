# This file is part of SwiftWAL, a tool to integrate PostgreSQL
# filesystem level backups, WAL archiving and point-in-time recovery
# with OpenStack Swift storage.
# Copyright 2013 Canonical Ltd.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3, as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranties of
# MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR
# PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from setuptools import setup

import swiftwal


setup(
    name='swiftwal',
    version=swiftwal.__version__,
    description='PostgreSQL backups, WAL archiving & PITR to OpenStack Swift',
    long_description=open('README.txt','r').read(),
    author='Stuart Bishop',
    author_email='stuart.bishop@canonical.com',
    url='https://launchpad.net/swiftwal',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Environment :: Console',
        'Environment :: OpenStack',
        'Intended Audience :: System Administrators',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        ## Python 3 support blocked on python-swiftclient and
        ## python-keystoneclient dependencies.
        ## 'Programming Language :: Python :: 3',
        ## 'Programming Language :: Python :: 3.3',
        'Topic :: Database',
        'Topic :: System :: Archiving :: Backup',
        'Topic :: System :: Recovery Tools',
        'Topic :: System :: Systems Administration',
        ],
    keywords="postgresql postgres wal pitr backup",
    install_requires=[
        'python-swiftclient >= 1.3.0', 'python-keystoneclient', 'argparse'],
    packages=['swiftwal'],
    entry_points=dict(console_scripts=['swiftwal=swiftwal.commands:main']),
    zip_safe=True,
    )
