#!/usr/bin/env python

#-----------------------------------------------------------------------------
# Copyright (c) 2013, The BiPy Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#-----------------------------------------------------------------------------

__credits__ = ["Daniel McDonald", "Jai Ram Rideout", "Yoshiki Vazquez Baeza"]

import os
import subprocess

class Version(object):
    """Represent module version information
    
    This is inspired by Python's sys.version_info
    """
    def __init__(self, package, major, minor, micro=None, releaselevel=None, init_file=None):
        if not isinstance(package, str):
            raise TypeError("Package must be a string")

        if not isinstance(major, int):
            raise TypeError("Major version must be an integer")

        if not isinstance(minor, int):
            raise TypeError("Minor version must be an integer")

        if micro is not None and not isinstance(micro, int):
            raise TypeError("Micro version must be an integer")

        if releaselevel is not None and not isinstance(releaselevel, str):
            raise TypeError("Releaselevel must be a string")

        if init_file is not None and not os.path.exists(init_file):
            raise ValueError("init_file must exist if provided")

        self.package = package
        self.major = major
        self.minor = minor
        self.micro = micro
        self.releaselevel = releaselevel
        self.init_file = init_file

    @property
    def mmm(self):
        """major.minor.micro version string"""
        if self.micro is None:
            return "%d.%d" % (self.major, self.minor)
        else:
            return "%d.%d.%d" % (self.major, self.minor, self.micro)

    def __str__(self):
        """Return a version string"""
        if self.micro is None:
            base = "%d.%d" % (self.major, self.minor)
        else:
            base = "%d.%d.%d" % (self.major, self.minor, self.micro)

        if self.releaselevel is not None:
            base = "%s-%s" % (base, self.releaselevel)

        git_branch = self.git_branch()
        git_sha1 = self.git_sha1()

        if git_branch is not None:
            return "%s, %s@%s" % (base, git_branch, git_sha1)
        else:
            return base

    def __repr__(self):
        """Return version information similar to Python's sys.version_info"""
        name = "%s_version" % self.package

        major = "major=%d" % self.major
        minor = "minor=%d" % self.minor

        items = [major, minor]
        if self.micro is not None:
            items.append("micro=%s" % self.micro)

        if self.releaselevel is not None:
            items.append("releaselevel='%s'" % self.releaselevel)

        git_branch = self.git_branch()
        git_sha1 = self.git_sha1(truncate=False)

        if git_branch is not None:
            git_branch = "git_branch='%s'" % git_branch
            git_sha1 = "git_sha1='%s'" % git_sha1
            items.append(git_branch)
            items.append(git_sha1)

        return "%s(%s)" % (name, ', '.join(items))

    def git_branch(self):
        """Get the current branch (if applicable)

        This code was adapted from QIIME. The author, Yoshiki Vazquez Baeza has
        given explicit permission for this code to be licensed under BSD. The
        discussion can be found here https://github.com/wasade/verman/issues/1
        """
        if self.init_file is None:
            return None

        pkg_dir = self.package_dir()
        
        branch_cmd = 'git --git-dir %s/.git rev-parse --abbrev-ref HEAD' %\
            (pkg_dir)
        branch_o, branch_e, branch_r = self.verman_system_call(branch_cmd)
        git_branch = branch_o.strip()

        if self._is_valid_git_refname(git_branch):
            return git_branch
        else:
            return None

    def git_sha1(self, truncate=True):
        """Get the current git SHA1 (if applicable)

        This code was adapted from QIIME. The author, Yoshiki Vazquez Baeza has
        given explicit permission for this code to be licensed under BSD. The
        discussion can be found here https://github.com/wasade/verman/issues/1
        """
        if self.init_file is None:
            return None

        pkg_dir = self.package_dir()

        sha_cmd = 'git --git-dir %s/.git rev-parse HEAD' % (pkg_dir)
        sha_o, sha_e, sha_r = self.verman_system_call(sha_cmd)
        git_sha = sha_o.strip()

        if self._is_valid_git_sha1(git_sha):
            if truncate:
                return git_sha[0:7]
            else:
                return git_sha
        else:
            return None

    def _is_valid_git_refname(self, refname):
        """check if a string is a valid branch-name/ref-name for git

        Input:
        refname: string to validate

        Output:
        True if 'refname' is a valid branch name in git. False if it fails to
        meet any of the criteria described in the man page for
        'git check-ref-format', also see:

        http://www.kernel.org/pub/software/scm/git/docs/git-check-ref-format.html

        This code was adapted from QIIME. The author, Yoshiki Vazquez Baeza has
        given explicit permission for this code to be licensed under BSD. The
        discussion can be found here https://github.com/wasade/verman/issues/1
        """
        if len(refname) == 0:
            return False

        # git imposes a few requirements to accept a string as a
        # refname/branch-name

        # They can include slash / for hierarchical (directory) grouping, but no
        # slash-separated component can begin with a dot . or end with the
        # sequence .lock
        if (len([True for element in refname.split('/')
                if element.startswith('.') or element.endswith('.lock')]) != 0):
            return False

        # They cannot have two consecutive dots .. anywhere
        if '..' in refname:
            return False

        # They cannot have ASCII control characters (i.e. bytes whose values are
        # lower than \040, or \177 DEL), space, tilde, caret ^, or colon :
        # anywhere
        if len([True for refname_char in refname if ord(refname_char) < 40 or
                ord(refname_char) == 177]) != 0:
            return False
        if ' ' in refname or '~' in refname or '^' in refname or ':' in refname:
            return False

        # They cannot have question-mark ?, asterisk *, or open bracket [
        # anywhere
        if '?' in refname or '*' in refname or '[' in refname:
            return False

        # They cannot begin or end with a slash / or contain multiple
        # consecutive slashes
        if refname.startswith('/') or refname.endswith('/') or '//' in refname:
            return False

        # They cannot end with a dot ..
        if refname.endswith('.'):
            return False

        # They cannot contain a sequence @{
        if '@{' in refname:
            return False

        # They cannot contain a \
        if '\\' in refname:
            return False

        return True

    def _is_valid_git_sha1(self, possible_hash):
        """check if a string is a valid git sha1 string

        Input:
        possible_hash: string to validate

        Output:
        True if the string has 40 characters and is an hexadecimal number, False
        otherwise.

        This code was adapted from QIIME. The author, Yoshiki Vazquez Baeza has
        given explicit permission for this code to be licensed under BSD. The
        discussion can be found here https://github.com/wasade/verman/issues/1
        """

        if len(possible_hash) != 40:
            return False
        try:
            _ = int(possible_hash, 16)
        except ValueError:
            return False

        return True

    def package_dir(self):
        """Returns the top-level package directory

        This code was adapted from QIIME. The author, Greg Caporaso, has given
        explicit permission for this code to be licensed under BSD. The
        discussion can be found here: https://github.com/wasade/verman/issues/1
        """
        # Get the full path of the module containing an instance of Version
        if self.init_file is None:
            return None

        current_file_path = os.path.abspath(self.init_file)

        # Get the directory
        current_dir_path = os.path.dirname(current_file_path)

        # Return the directory containing the directory containing the instance
        return os.path.dirname(current_dir_path)

    def verman_system_call(self, cmd):
        """Issue a system call

        This code is based off of pyqi's pyqi_system_call
        """
        proc = subprocess.Popen(cmd, shell=True, universal_newlines=True,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # communicate pulls all stdout/stderr from the PIPEs to
        # avoid blocking -- don't remove this line!
        stdout, stderr = proc.communicate()
        return_value = proc.returncode
        return stdout, stderr, return_value

verman_version = Version("verman", 1, 1, init_file=__file__)
__version__ = verman_version.mmm
