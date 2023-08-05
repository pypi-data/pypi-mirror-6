"""cwtags packaging information.

:organization: Logilab
:copyright: 2009-2013 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
:license: General Public License version 2 - http://www.gnu.org/licenses
"""
__docformat__ = "restructuredtext en"
from glob import glob

# pylint: disable-msg=W0622

# package name
modname = 'cwtags'

# release version
numversion = (1, 0, 0)
version = '.'.join(str(num) for num in numversion)

# license and copyright
license = 'GPL'
copyright = 'Copyright (c) '+' '.join([line.split(': ')[-1]for line in __doc__.splitlines()[3:5]])

# short and long description
short_desc = "a small convenience html tags lib for CubicWeb"
long_desc = """a small convenience html tags lib for CubicWeb"""

# author name and email
author = "Logilab"
author_email = "contact@logilab.fr"

# home page
web = "http://www.cubicweb.org/project/%s" % modname

# mailing list
mailinglist = 'mailto://cubicweb@lists.cubicweb.org'

# download place
ftp = "ftp://ftp.logilab.org/pub/%s" % modname

# is there some directories to include with the source installation
include_dirs = []

# executable

scripts = []

pyversions = ['2.5']

