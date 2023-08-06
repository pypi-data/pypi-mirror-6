# Copyright (C) 2010 by the Free Software Foundation, Inc.
#
# This file is part of mailman.client.
#
# mailman.client is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# mailman.client is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License
# for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with mailman.client.  If not, see <http://www.gnu.org/licenses/>.

import distribute_setup
distribute_setup.use_setuptools()

from setup_helpers import (
    description, find_doctests, get_version, long_description, require_python)
from setuptools import setup, find_packages


require_python(0x20600f0)


setup(
    name='mailmanclient',
    version='1.0.0b1',
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    include_package_data=True,
    maintainer='Barry Warsaw',
    maintainer_email='barry@list.org',
    description=description('README.txt'),
    long_description=long_description(
        'src/mailmanclient/README.txt',
        'src/mailmanclient/NEWS.txt'),
    license='LGPLv3',
    url='http://launchpad.net/mailman.client',
    download_url='https://launchpad.net/mailman.client/+download',
    # Auto-conversion to Python 3.
    use_2to3=True,
    convert_2to3_doctests=find_doctests(),
    install_requires=['httplib2', 'mock', ],
)
