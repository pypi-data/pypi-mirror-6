#!/usr/bin/env python

# Copyright (C) 2011-2012 CRS4.
#
# This file is part of Seal.
#
# Seal is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Seal is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Seal.  If not, see <http://www.gnu.org/licenses/>.


import os
import sys

import seal.lib.aligner.bwa.bwa_core as bwa

def usage_error(msg = None):
    if msg:
        print >>sys.stderr, msg
    print >>sys.stderr, "Usage: %s <index root name>" % sys.argv[0]
    sys.exit(1)

def main(args):
    if len(args) != 2:
        usage_error()

    index = args[1]
    if os.path.exists(index + ".sax"):
        usage_error("%s.sax exists.  Refusing to overwrite it." % index)
    elif os.path.exists(index + ".rsax"):
        usage_error("%s.rsax exists.  Refusing to overwrite it." % index)

    print >>sys.stderr, "Converting indexed reference at %s.  This might take a while...." % index
    bwa.make_suffix_arrays_for_mmap(index)
    print >>sys.stderr, "done!"
    return 0
