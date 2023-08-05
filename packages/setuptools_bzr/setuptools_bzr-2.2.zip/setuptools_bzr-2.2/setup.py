# Copyright (C) 2007-2010 by Barry A. Warsaw
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301,
# USA.

from setuptools import setup, find_packages
from setuptools_bzr import __version__


setup(
    name            = 'setuptools_bzr',
    version         = __version__,
    description     = 'setuptools plugin for bzr',
    author          = 'Barry Warsaw',
    author_email    = 'barry@python.org',
    maintainer      = 'Richard Gomes',
    maintainer_email= 'rgomes.info@gmail.com',
    license         = 'LGPLv3',
    # For historical reasons, the code lives under a different project name.
    url             = 'https://launchpad.net/setuptoolsbzr',
    keywords        = 'distutils setuptools setup bzr bazaar',
    packages        = find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.4",
        "Programming Language :: Python :: 2.5",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.1",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU Lesser General Public License v2 or later (LGPLv2+)",
        "Topic :: Software Development :: Version Control",
        "Framework :: Setuptools Plugin",
    ],
    entry_points    = {
        'setuptools.file_finders': [
            'bzr = setuptools_bzr:find_files_for_bzr',
            ],
        },
    )
