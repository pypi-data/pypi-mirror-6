#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# ***** BEGIN LICENSE BLOCK *****
# Copyright (C) 2012-2013  Hayaki Saito <user@zuse.jp>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# ***** END LICENSE BLOCK *****

import sskk.mode as mode
import sskk.input as input
import sskk.romanrule as romanrule
import sskk.kanadb as kanadb
import sskk.eisuudb as eisuudb
import sskk.dictionary as dictionary
import sskk.charbuf as charbuf
import sskk.word as word
import sskk.output as output

import doctest

_dirty = False
for m in (mode,
          input,
          romanrule,
          kanadb,
          eisuudb,
          dictionary,
          charbuf,
          word,
          output):
    failure_count, test_count = doctest.testmod(m)
    if failure_count > 0:
        _dirty = True
if _dirty:
    raise ImportError("test failed.")

print "smoke tests succeeded."
    
    
