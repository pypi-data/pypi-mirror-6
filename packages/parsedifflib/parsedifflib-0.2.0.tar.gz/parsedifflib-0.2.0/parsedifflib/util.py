# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id$
# auth: metagriffin <mg.github@uberdev.org>
# date: 2013/12/10
# copy: (C) Copyright 2013-EOT metagriffin -- see LICENSE.txt
#------------------------------------------------------------------------------
# This software is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This software is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see http://www.gnu.org/licenses/.
#------------------------------------------------------------------------------

class Source(object):
  '''
  Source is a helper object with input streams to:

  a. Normalize line endings to "\n"
  b. Provide line-oriented stream peeking.
  '''
  def __init__(self, stream):
    self.stream  = stream
    self.cache   = []
    self.curline = 1
  def readline(self):
    self.curline += 1
    if self.cache:
      return self.cache.pop()
    ret = self.stream.readline()
    if not ret:
      return ret
    if ret.endswith('\r'):
      ret = ret[:-1] + '\n'
    elif ret.endswith('\r\n'):
      ret = ret[:-2] + '\n'
    return ret
  def readlines(self, count):
    return [self.readline() for idx in range(count)]
  def pushline(self, line):
    self.curline -= 1
    if line:
      self.cache.append(line)
  def pushlines(self, lines):
    for line in reversed(lines):
      self.pushline(line)
  def peekline(self):
    line = self.readline()
    self.pushline(line)
    return line
  def peeklines(self, count):
    ret = self.readlines(count)
    self.pushlines(ret)
    return ret

#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------
