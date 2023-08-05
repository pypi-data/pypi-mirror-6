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

#------------------------------------------------------------------------------
class Event(object):

  PATCH_START           = 10
  PATCH_END             = 11
  ENTRY_START           = 20
  ENTRY_END             = 21
  LINE_LOC              = 30
  LINE_SAME             = 31
  LINE_ADD              = 32
  LINE_DELETE           = 33
  LINE_NOTE             = 34
  PROPENTRY             = 40
  PROPENTRY_START       = 41
  PROPENTRY_END         = 42
  SEGMENT_SAME          = 51
  SEGMENT_ADD           = 52
  SEGMENT_DELETE        = 53

#------------------------------------------------------------------------------
class SimpleRepr(object):
  def __repr__(self):
    ret = '<parsedifflib.%s' % (self.__class__.__name__,)
    for key in dir(self):
      if key.startswith('_'):
        continue
      try:
        val = getattr(self, key, None)
      except AttributeError:
        continue
      if val is not None:
        ret += ' %s=%r' % (key, val)
    return ret + '>'

#------------------------------------------------------------------------------
class Patch(SimpleRepr): pass

#------------------------------------------------------------------------------
class Entry(SimpleRepr):

  TYPE_CONTENT          = 1
  TYPE_PROPERTY         = 2

  def __init__(self, type,
               source=None, target=None,
               srcsig=None, tgtsig=None,
               comment=None):
    self.type    = type
    self.source  = source
    self.target  = target
    self.srcsig  = srcsig
    self.tgtsig  = tgtsig
    self.comment = comment

#------------------------------------------------------------------------------
class Line(SimpleRepr):
  def __init__(self, line, oldnum=None, newnum=None, segments=None):
    self.line     = line
    self.oldnum   = oldnum
    self.newnum   = newnum
    self.segments = segments

#------------------------------------------------------------------------------
class Segment(SimpleRepr):
  def __init__(self, text):
    self.text = text
  def __repr__(self):
    return repr(self.text)

#------------------------------------------------------------------------------
class PropertyEntry(SimpleRepr):
  def __init__(self, head, old=None, new=None):
    self.head = head
    self.old  = old
    self.new  = new

#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------
