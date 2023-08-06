"""
The versioncontrol sub-package provides an abstraction layer around different
revision/version control systems. Only the functionality required for recording
version numbers and switching the working copy between different versions is
wrapped - for more complex tasks such as merging, branching, etc., the
version control tool should be used directly.

Sub-modules
-----------

base        - defines the base WorkingCopy and Repository classes
_mercurial  - defines MercurialWorkingCopy and MercurialRepository classes
_subversion - defines SubversionWorkingCopy and SubversionRepository classes
_git        - defines GitWorkingCopy and GitRepository classes
_bazaar     - defines BazaarWorkingCopy and BazaarRepository classes

Exceptions
----------

VersionControlError - generic Exception class for problems with version control

Functions
---------

get_working_copy() - given a filesystem path, determine if a working copy exists
                     and return an appropriate WorkingCopy object if so.
get_repository()   - determine whether a revision control system repository
                     exists at a given URL and return an appropriate Repository
                     object if so.


:copyright: Copyright 2006-2014 by the Sumatra team, see doc/authors.txt
:license: CeCILL, see LICENSE for details.
"""

import sys
import os

from .base import VersionControlError, UncommittedModificationsError


vcs_list = []
vcs_unavailable = []

for vcs in ['mercurial', 'subversion', 'git', 'bazaar']:
    try:
        __import__('sumatra.versioncontrol._%s' % vcs)
        vcs_list.append(sys.modules['sumatra.versioncontrol._%s' % vcs])
    except ImportError as err:
        vcs_unavailable.append(vcs)


def vcs_err_msg():
    err_msg = ""
    if vcs_list:
        err_msg += "\nTried: %s" % ", ".join(vcs.__name__.split(".")[-1][1:].title() for vcs in vcs_list)
    if vcs_unavailable:
        err_msg += "\nNot installed or missing Python bindings: %s" % ", ".join(vcs.title() for vcs in vcs_unavailable)
    return err_msg


def get_working_copy(path=None):
    """
    Return a :class:`WorkingCopy` object which represents, and enables limited
    interaction with, the version control working copy at *path*.

    If *path* is not specified, the current working directory is used.
    If no working copy is found at *path*, raises a :class:`VersionControlError`.
    """
    path = path or os.getcwd()
    if vcs_list:
        for vcs in vcs_list:
            if vcs.may_have_working_copy(path):
                return vcs.get_working_copy(path)
        err_msg = "No working copy found at %s." % path + vcs_err_msg()
        raise VersionControlError(err_msg)
    else:
        err_msg = "No version control systems found. Please see the documentation for information on installing the required packages."
        raise VersionControlError(err_msg)


def get_repository(url):
    """
    Return a :class:`Repository` object which represents, and enables limited
    interaction with, the version control repository at *url*.

    If no repository is found at *url*, raises a :class:`VersionControlError`.
    """
    if url:
        repos = None
        if vcs_list:
            for vcs in vcs_list:
                try:
                    repos = vcs.get_repository(url)
                    break
                except Exception as e:
                    pass
        else:
            raise VersionControlError("No version control systems found.")
        if repos is None:
            raise VersionControlError("Can't find repository at URL '%s'" % url + vcs_err_msg())
        else:
            return repos
    else:
        working_copy = get_working_copy()
        if working_copy:
            return working_copy.repository
        else:
            return None
