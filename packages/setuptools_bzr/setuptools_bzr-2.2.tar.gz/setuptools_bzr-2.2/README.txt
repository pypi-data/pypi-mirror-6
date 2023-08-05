setuptools_bzr - A setuptools plugin for Bazaar
Copyright (C) 2007-2008 by Barry A. Warsaw
Licensed under the terms of the LGPL v2.


License
=======

This program is free software; you can redistribute it and/or modify it under
the terms of the GNU Lesser General Public License as published by the Free
Software Foundation; either version 2 of the License, or (at your option) any
later version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
details.

You should have received a copy of the GNU Lesser General Public License along
with this program; if not, write to the Free Software Foundation, Inc., 51
Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.


Description
===========

Python's setuptools_ package provides a higher-level API for building Python
packages, integrating with the Cheeseshop_ and for building compact
distribution packages such as eggs_.  By default, setuptools supports
Subversion_ and CVS_.  The setuptools_bzr package extends this support to
projects maintained under the `Bazaar distributed revision control system`_.

.. _setuptools: http://peak.telecommunity.com/DevCenter/setuptools
.. _Cheeseshop: http://pypi.python.org
.. _eggs: http://peak.telecommunity.com/DevCenter/PythonEggs
.. _Subversion: http://subversion.tigris.org/
.. _CVS: http://www.nongnu.org/cvs/
.. _`Bazaar distributed revision control system`: http://bazaar-vcs.org


Usage
=====

Use the setuptools_bzr plugin by adding the following to your `setup()`
function::

    setup_requires = [
        'setuptools_bzr',
        ],

See this package's own `setup.py` file for an example.  You must either have
bzrlib_ installed in your Python or access to the `bzr(1)` command line
program.


Contact information
===================

Author: Barry Warsaw <barry@python.org>
Maintainer: Richard Gomes <rgomes.info@gmail.com>

This package is developed on Launchpad_.  Please see the `project page`_ for
submitting bug reports.

.. _Launchpad: http://launchpad.net
.. `project page`_: https://launchpad.net/setuptoolsbzr
