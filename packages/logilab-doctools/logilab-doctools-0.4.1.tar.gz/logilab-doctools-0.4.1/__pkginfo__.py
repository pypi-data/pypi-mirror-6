# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
""" Copyright (c) 2003-2014 LOGILAB S.A. (Paris, FRANCE).
http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""

modname = "doctools"
distname = "logilab-doctools"
numversion = (0, 4, 1)
version = '.'.join([str(num) for num in numversion])

license = 'GPL'
copyright = '''Copyright (c) 2003-2014 LOGILAB S.A. (Paris, FRANCE).
http://www.logilab.fr/ -- mailto:contact@logilab.fr'''

author = "Logilab"
author_email = "contact@logilab.fr"

from os.path import join
scripts = [join('bin', name)
           for name in ('mkdoc', 'py2dbk', 'xml2dbk', 'mkfor')]

description = "tools used at Logilab to make documents"
long_desc = "Set of tools to help transforming documents in various formats."

web = "http://www.logilab.org/project/%s" % distname
ftp = "ftp://ftp.logilab.org/pub/%s" % modname
mailinglist = "mailto://management-projects@logilab.org"

subpackage_of = 'logilab'
subpackage_master = False

debian_name = 'logilab-doctools'
pyversions = ["2.5", "2.6", "2.7"]

include_dirs = ["data"]
