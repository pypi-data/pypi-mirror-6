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

from __future__ import print_function

"""setuptools plugin for projects maintained under Bazaar."""

__version__ = '2.2'
__all__ = [
    'find_files_for_bzr',
    ]


import os, sys
import subprocess

try:
    from bzrlib.branch import Branch
    from bzrlib.errors import NotBranchError
    from bzrlib.plugin import load_plugins
except ImportError:
    Branch = None


PY3 = sys.version[0] == "3"


if os.getenv('BZR_SETUPTOOLS_FORCE_CMD'):
    Branch = None


def bzrlib_get_children(path):
    """Use direct bzrlib calls to get child information."""
    # Be sure to register loom branch formats.
    load_plugins()
    # Open an existing branch which contains the url.
    branch, inpath = Branch.open_containing(path)
    branch.lock_read()
    try:
        # Get the inventory of the branch's last revision.
        inv = branch.repository.get_inventory(branch.last_revision())
        # Get the inventory entry for the path.
        entry = inv[inv.path2id(path)]
        # Return the names of the children.
        return [os.path.join(path, child) for child in list(entry.children.keys())]
    finally:
        branch.unlock()


def bzrlib_find_files_for_bzr(dirname):
    """Use direct bzrlib calls to recursively find versioned files."""
    bzrfiles = []
    search = [dirname]
    while search:
        current = search.pop(0)
        try:
            children = bzrlib_get_children(current)
        except NotBranchError:
            # Ignore this directory, it's not under bzr
            pass
        else:
            bzrfiles.extend(children)
            search.extend([child for child in children
                           if os.path.isdir(child)])
    return bzrfiles


def bzr_find_files_for_bzr(dirname):
    """Use the program bzr(1) to recursively find versioned files."""
    cmd = 'bzr ls --recursive --versioned ' + dirname
    try:
        proc = subprocess.Popen(cmd.split(),
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()
    except Exception as e:
        print('WARNING: bzr: {}'.format(e), file=sys.stderr)
        return []

    if not PY3:
        return stdout.splitlines()
    else:
        return (line.decode('utf-8') for line in stdout.splitlines())


def find_files_for_bzr(dirname):
    """Return the files found that are under bzr version control."""
    if Branch is None:
        paths = bzr_find_files_for_bzr(dirname)
    else:
        paths = bzrlib_find_files_for_bzr(dirname)
    return [path for path in paths if os.path.isfile(path)]
