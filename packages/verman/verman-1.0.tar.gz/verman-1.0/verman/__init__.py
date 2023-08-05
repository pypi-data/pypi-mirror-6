#!/usr/bin/env python

#-----------------------------------------------------------------------------
# Copyright (c) 2013, The BiPy Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#-----------------------------------------------------------------------------

__credits__ = ["Daniel McDonald", "Jai Ram Rideout"]

class Version(object):
    """Represent module version information
    
    This is inspired by Python's sys.version_info
    """
    def __init__(self, package, major, minor, micro=None, releaselevel=None):
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

        self.package = package
        self.major = major
        self.minor = minor
        self.micro = micro
        self.releaselevel = releaselevel

    def __str__(self):
        """Return a version string"""
        if self.micro is None:
            base = "%d.%d" % (self.major, self.minor)
        else:
            base = "%d.%d.%d" % (self.major, self.minor, self.micro)

        if self.releaselevel is None:
            return base
        else:
            return "%s-%s" % (base, self.releaselevel)

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

        return "%s(%s)" % (name, ', '.join(items))

verman_version = Version("verman", 1, 0)
__version__ = str(verman_version)
