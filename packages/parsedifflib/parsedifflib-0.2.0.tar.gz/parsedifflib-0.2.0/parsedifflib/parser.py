# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id$
# auth: metagriffin <mg.github@uberdev.org>
# date: 2013/11/27
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

import six, morph, re, difflib
from aadict import aadict

from . import api
from .util import Source

#------------------------------------------------------------------------------
class ParseError(Exception):
  def __init__(self, msg, stage):
    super(ParseError, self).__init__(
      msg + ' on line %r: %s' % (stage.source.curline, stage.source.peekline()))
class InvalidChangeError(ParseError): pass

#------------------------------------------------------------------------------
def parse_svnlook(data, settings=None):
  stage = aadict(options=aadict(
    lineNumbers          = False,
    intraLineDiff        = False,
    intraLineCompact     = False,
    propertyUnifiedDiff  = False,
    ))
  stage.options.update(settings or {})
  if morph.isstr(data):
    data = six.StringIO(data)
  stage.source = Source(data)
  events = _parse(stage)
  if stage.options.propertyUnifiedDiff:
    events = _addPropertyUnifiedDiff(stage, events)
  if stage.options.lineNumbers:
    events = _addLineNumbers(stage, events)
  if stage.options.intraLineDiff:
    events = _addIntraLineDiff(stage, events)
  for evt in events:
    yield evt

#------------------------------------------------------------------------------
_addLineNumbers_loc_re = re.compile('^@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@$')
def _addLineNumbers(stage, events):
  pos = [None, None]
  for etype, obj in events:
    if etype == api.Event.LINE_LOC:
      match = _addLineNumbers_loc_re.match(obj.line)
      if not match:
        raise ValueError('invalid location line: %r' % (obj.line,))
      pos = map(int, match.groups())
    if etype == api.Event.LINE_SAME:
      obj.oldnum = pos[0]
      obj.newnum = pos[1]
      pos[0] += 1
      pos[1] += 1
    if etype == api.Event.LINE_ADD:
      obj.newnum = pos[1]
      pos[1] += 1
    if etype == api.Event.LINE_DELETE:
      obj.oldnum = pos[0]
      pos[0] += 1
    yield etype, obj

#------------------------------------------------------------------------------
def _addIntraLineDiff(stage, events):
  buf = []
  def handleBuffer(buf):
    # todo: a *very* smart implementation would investigate consecutive
    # adds and deletes to determine if they should be interleaved...
    for idx, cur in enumerate(buf):
      if cur[0] == api.Event.LINE_DELETE \
          and ( idx == 0 or buf[idx - 1][0] != api.Event.LINE_DELETE ) \
          and ( idx + 1 < len(buf) ) and buf[idx + 1][0] == api.Event.LINE_ADD \
          and ( ( idx + 2 >= len(buf) ) or buf[idx + 2][0] != api.Event.LINE_ADD ):
        _calcIntraLineDiff(stage, cur[1], buf[idx + 1][1])
    buf.reverse()
    while buf:
      yield buf.pop()
  for typ, obj in events:
    if typ not in (api.Event.LINE_ADD, api.Event.LINE_DELETE):
      for evt in handleBuffer(buf):
        yield evt
      yield typ, obj
      continue
    buf.append((typ, obj))
    continue
  # paranoia. this should never be needed, since there should have
  # been, at the very least, a terminal PATCH_END event triggering a
  # handleBuffer() earlier.
  for evt in handleBuffer(buf):
    yield evt

#------------------------------------------------------------------------------
def _calcIntraLineDiff(stage, rem, add):
  seq = difflib.SequenceMatcher(a=rem.line, b=add.line)
  rems = []
  adds = []
  for op in seq.get_opcodes():
    if op[0] == 'equal':
      rems.append((api.Event.SEGMENT_SAME, api.Segment(rem.line[op[1]:op[2]])))
      adds.append((api.Event.SEGMENT_SAME, api.Segment(add.line[op[3]:op[4]])))
      continue
    if op[0] == 'insert':
      adds.append((api.Event.SEGMENT_ADD, api.Segment(add.line[op[3]:op[4]])))
      continue
    if op[0] == 'delete':
      rems.append((api.Event.SEGMENT_DELETE, api.Segment(rem.line[op[1]:op[2]])))
      continue
    if op[0] == 'replace':
      rems.append((api.Event.SEGMENT_DELETE, api.Segment(rem.line[op[1]:op[2]])))
      adds.append((api.Event.SEGMENT_ADD, api.Segment(add.line[op[3]:op[4]])))
      continue
    raise ValueError('unexpected difflib opcode %r' % (op[0],))
  rem.segments = reduce(_collapseSegments, rems, [])
  add.segments = reduce(_collapseSegments, adds, [])

#------------------------------------------------------------------------------
def _collapseSegments(ret, item):
  if not ret or ret[-1][0] != item[0]:
    return ret + [item]
  ret[-1][1].text += item[1].text
  return ret

#------------------------------------------------------------------------------
def _addPropertyUnifiedDiff(stage, events):
  for typ, prop in events:
    if typ != api.Event.PROPENTRY:
      yield typ, prop
      continue
    yield api.Event.PROPENTRY_START, prop
    old = prop.old.split('\n') if prop.old is not None else []
    new = prop.new.split('\n') if prop.new is not None else []
    for ops in difflib.SequenceMatcher(a=old, b=new).get_grouped_opcodes():
      yield api.Event.LINE_LOC, api.Line('@@ -%d,%d +%d,%d @@' % (
        ops[0][1] + 1, ops[-1][2] - ops[0][1],
        ops[0][3] + 1, ops[-1][4] - ops[0][3]))
      for op in ops:
        if op[0] == 'equal':
          for idx in range(op[1], op[2]):
            yield api.Event.LINE_SAME, api.Line(old[idx])
          continue
        if op[0] == 'insert':
          for idx in range(op[3], op[4]):
            yield api.Event.LINE_ADD, api.Line(new[idx])
          continue
        if op[0] == 'delete':
          for idx in range(op[1], op[2]):
            yield api.Event.LINE_DELETE, api.Line(old[idx])
          continue
        if op[0] == 'replace':
          for idx in range(op[1], op[2]):
            yield api.Event.LINE_DELETE, api.Line(old[idx])
          for idx in range(op[3], op[4]):
            yield api.Event.LINE_ADD, api.Line(new[idx])
          continue
        raise ValueError('unexpected difflib opcode %r' % (op[0],))
    yield api.Event.PROPENTRY_END, prop

#------------------------------------------------------------------------------
def _parse(stage):
  stage.patch = api.Patch()
  yield api.Event.PATCH_START, stage.patch
  while stage.source.peekline():
    for evt in _parse_change(stage):
      yield evt
  yield api.Event.PATCH_END, stage.patch

#------------------------------------------------------------------------------
def _parse_change(stage):
  found = False
  for evt in _parse_svnlook_contentChange(stage):
    found = True
    yield evt
  if found:
    return
  for evt in _parse_svnlook_propertyChange(stage):
    found = True
    yield evt
  if found:
    return
  raise InvalidChangeError('invalid source', stage)

#------------------------------------------------------------------------------
def _parse_svnlook_contentChange(stage):
  peek = stage.source.peeklines(2)
  if not peek[0].strip() or peek[1] != ( '=' * 67 + '\n' ):
    return
  comment, sep, old, new = stage.source.readlines(4)

  # check for binary file events
  if old == '(Binary files differ)\n' and new == '\n':
    entry = api.Entry(api.Entry.TYPE_CONTENT, comment=comment[:-1])
    yield api.Event.ENTRY_START, entry
    yield api.Event.LINE_NOTE, api.Line(old[:-1])
    yield api.Event.ENTRY_END, entry
    return

  # ensure proper begin declaration
  if not ( old.startswith('--- ') and new.startswith('+++ ') ):

    # creating this early, just in case it is needed...
    entry = api.Entry(api.Entry.TYPE_CONTENT, comment=comment[:-1])

    # check for empty file event (ie. end of diff)
    if not old and not new:
      yield api.Event.ENTRY_START, entry
      yield api.Event.LINE_NOTE, api.Line('(Empty file)')
      yield api.Event.ENTRY_END, entry
      return

    # check for empty file event (ie. parseable entries follow)
    stage.source.pushlines([old, new])
    for evt in _parse_change(stage):
      if entry is not None:
        yield api.Event.ENTRY_START, entry
        yield api.Event.LINE_NOTE, api.Line('(Empty file)')
        yield api.Event.ENTRY_END, entry
        entry = None
      yield evt

    if entry is not None:
      stage.source.pushlines([comment, sep])
    return

  # and now parse the changes
  entry = api.Entry(
    api.Entry.TYPE_CONTENT,
    source = old[4:].split('\t', 1)[0],
    target = new[4:].split('\t', 1)[0],
    srcsig = old[4:].split('\t', 1)[1][:-1],
    tgtsig = new[4:].split('\t', 1)[1][:-1],
    comment = comment[:-1])
  yield api.Event.ENTRY_START, entry

  while True:
    line = stage.source.readline()
    if not line or line == '\n':
      break
    if line.startswith('@@ '):
      yield api.Event.LINE_LOC, api.Line(line.strip())
      continue
    if line.startswith(' '):
      yield api.Event.LINE_SAME, api.Line(line[1:-1])
      continue
    if line.startswith('\\') or line.startswith('/'):
      yield api.Event.LINE_NOTE, api.Line(line[:-1])
      continue
    if line.startswith('+'):
      yield api.Event.LINE_ADD, api.Line(line[1:-1])
      continue
    if line.startswith('-'):
      yield api.Event.LINE_DELETE, api.Line(line[1:-1])
      continue
    raise ParseError('unexpected prefix', stage)

  yield api.Event.ENTRY_END, entry

propChangeEntry_re = re.compile('^(Added|Modified|Deleted): (.+)$')

#------------------------------------------------------------------------------
def _parse_svnlook_propertyChange(stage):
  peek = stage.source.peeklines(3)
  if peek[0] != '\n' or not peek[1].startswith('Property changes on: ') \
      or peek[2] != ( '_' * 67 + '\n' ):
    return
  nl, comment, sep = stage.source.readlines(3)

  entry = api.Entry(api.Entry.TYPE_PROPERTY, comment=comment[:-1])
  yield api.Event.ENTRY_START, entry

  prop = api.PropertyEntry(None)

  while True:
    line = stage.source.readline()
    if propChangeEntry_re.match(line):
      if prop.head:
        if prop.old is None and prop.new is None:
          raise ParseError('unexpected property entry (head)', stage)
        yield api.Event.PROPENTRY, prop
      prop.head, prop.old, prop.new = line[:-1], None, None
      continue
    if not prop.head:
      raise ParseError('unexpected property entry (no-head)', stage)
    if line.startswith('   - '):
      if prop.old:
        raise ParseError('unexpected property entry (repeat-old)', stage)
      if prop.new:
        raise ParseError('unexpected property entry (new-first)', stage)
      prop.old = line[5:-1]
      continue
    if line.startswith('   + '):
      if prop.new:
        raise ParseError('unexpected property entry (repeat-new)', stage)
      prop.new = line[5:-1]
      continue
    if line == '\n':
      if not stage.source.peekline():
        if prop.old is None and prop.new is None:
          raise ParseError('unexpected EOF in property entry', stage)
        yield api.Event.PROPENTRY, prop
        yield api.Event.ENTRY_END, entry
        return
      try:
        for evt in _parse_change(stage):
          if prop is not None:
            if prop.old is None and prop.new is None:
              raise ParseError('unexpected property entry (empty)', stage)
            yield api.Event.PROPENTRY, prop
            yield api.Event.ENTRY_END, entry
            prop = None
          yield evt
        return
      except InvalidChangeError:
        pass
    if prop.new is not None:
      prop.new += '\n' + line[:-1]
      continue
    if prop.old is not None:
      prop.old += '\n' + line[:-1]
      continue
    raise ParseError('unexpected property entry (no-new-or-old)', stage)

  raise ParseError('unexpected property entry (no-term)', stage)

#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------
