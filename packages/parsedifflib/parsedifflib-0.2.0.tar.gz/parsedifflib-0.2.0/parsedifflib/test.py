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

import os, unittest, asset, re
from aadict import aadict

import parsedifflib
from parsedifflib import api

heredir = os.path.abspath(os.path.dirname(__file__))
datadir = os.path.join(heredir, 'data')

#------------------------------------------------------------------------------
def wrap(data, start, end):
  data = (end + '\n' + start).join(data.split('\n'))
  return start + data + end
def colorize(data, style='svnlook'):
  spec = aadict(
    add    = lambda data: wrap(data, '[1;34m', '[0;0m'),
    delete = lambda data: wrap(data, '[1;31m', '[0;0m'),
    note   = lambda data: wrap(data, '[1;35m', '[0;0m'),
    plain  = lambda data: wrap(data, '[1;37m', '[0;0m'),
    meta   = lambda data: wrap(data, '[1;32m', '[0;0m'),
    )
  if style != 'svnlook':
    raise ValueError('unsupported colorization style: ' + style)
  ret = []
  ent = 0

  for etype, obj in parsedifflib.parse_svnlook(data):

    if etype in (
        parsedifflib.Event.PATCH_START,
        parsedifflib.Event.PATCH_END,
        ):
      continue

    elif etype == parsedifflib.Event.ENTRY_START:
      ent += 1
      if ent > 1:
        ret.append(spec.plain(''))
      if obj.type == parsedifflib.Entry.TYPE_PROPERTY:
        ret.append(spec.plain(''))
      ret.append(spec.meta(obj.comment))
      if obj.type == parsedifflib.Entry.TYPE_PROPERTY:
        ret.append(spec.meta('_' * 67))
      else:
        ret.append(spec.meta('=' * 67))
      if obj.source:
        ret.append(spec.delete('--- {}\t{}'.format(obj.source, obj.srcsig or '')))
      if obj.target:
        ret.append(spec.add('+++ {}\t{}'.format(obj.target, obj.tgtsig or '')))

    elif etype == parsedifflib.Event.ENTRY_END:
      if obj.type == parsedifflib.Entry.TYPE_PROPERTY:
        ret.append(spec.plain(''))
        # todo: HACK ALERT! i don't know why this is necessary. it appears
        # that sometimes svnlook does not always insert this blank line...
        ent = 0

    elif etype == parsedifflib.Event.LINE_LOC:
      ret.append(spec.note(obj.line))

    elif etype == parsedifflib.Event.LINE_NOTE:
      ret.append(spec.note(obj.line))

    elif etype == parsedifflib.Event.LINE_SAME:
      ret.append(spec.plain(' ' + obj.line))

    elif etype == parsedifflib.Event.LINE_DELETE:
      ret.append(spec.delete('-' + obj.line))

    elif etype == parsedifflib.Event.LINE_ADD:
      ret.append(spec.add('+' + obj.line))

    elif etype == parsedifflib.Event.PROPENTRY:
      ret.append(spec.meta(obj.head))
      if obj.old:
        ret.append(spec.delete('   - ' + obj.old))
      if obj.new:
        ret.append(spec.add('   + ' + obj.new))

    else:
      raise ValueError('unexpected event type: ' + repr(etype))


  return '\n'.join(ret) + '\n'

#------------------------------------------------------------------------------
class TestParseDiffLib(unittest.TestCase):

  maxDiff = None

  nietzsche_diff = '''\
Modified: Quotes/FriedrichNietzsche-TheWay.txt
===================================================================
--- Quotes/FriedrichNietzsche-TheWay.txt	1844-10-15 00:00:00 UTC (rev 1)
+++ Quotes/FriedrichNietzsche-TheWay.txt	1900-08-25 00:00:00 UTC (rev 2)
@@ -1,7 +1,7 @@
 You have your way. I have my
 way. As for the right way, the
 correct way, and the only way,
-it does not exist.
+it's definitely not your way ;).
 
   -- Friedrich Nietzsche
      1844 - 1900
'''

  propEntry_diff = '''\

Property changes on: property/file1.txt
___________________________________________________________________
Modified: test:property1
   - one line

(blank line above and below too)


   + one line
(blank line above removed)
(blank line below)



'''

  #----------------------------------------------------------------------------
  def test_raw(self):
    patch = api.Patch()
    ent1 = api.Entry(
      api.Entry.TYPE_CONTENT,
      'app/bin/runner', 'app/bin/runner',
      '2013-05-31 16:43:09 UTC (rev 2958)',
      '2013-05-31 17:54:22 UTC (rev 2959)',
      'Deleted: app/bin/runner')
    ent2 = api.Entry(
      api.Entry.TYPE_CONTENT,
      'app/setup.py', 'app/setup.py',
      '2013-05-31 16:43:09 UTC (rev 2958)',
      '2013-05-31 17:54:22 UTC (rev 2959)',
      'Modified: app/setup.py')
    ent3 = api.Entry(
      api.Entry.TYPE_CONTENT,
      'app/lib/python/MANIFEST', 'app/lib/python/MANIFEST',
      '2013-05-31 16:43:09 UTC (rev 2958)',
      '2013-05-31 17:54:22 UTC (rev 2959)',
      'Modified: app/lib/python/MANIFEST')
    ent4 = api.Entry(
      api.Entry.TYPE_CONTENT,
      comment = 'Added: app/lib/python/my_app-1.2.3.tar.gz')
    ent5 = api.Entry(
      api.Entry.TYPE_PROPERTY,
      comment = 'Property changes on: app/lib/python/my_app-1.2.3.tar.gz')
    chk = [
      (api.Event.PATCH_START, patch),
      (api.Event.ENTRY_START, ent1),
      (api.Event.LINE_LOC, api.Line('@@ -1,4 +0,0 @@')),
      (api.Event.LINE_DELETE, api.Line('#!/usr/bin/env python')),
      (api.Event.LINE_DELETE, api.Line('import sys')),
      (api.Event.LINE_DELETE, api.Line('from app.cli import main')),
      (api.Event.LINE_DELETE, api.Line('sys.exit(main())')),
      (api.Event.ENTRY_END, ent1),
      (api.Event.ENTRY_START, ent2),
      (api.Event.LINE_LOC, api.Line('@@ -80,7 +80,7 @@')),
      (api.Event.LINE_SAME, api.Line('  \'Shapely                  == 1.2.17\',')),
      (api.Event.LINE_SAME, api.Line('')),
      (api.Event.LINE_SAME, api.Line('  # message queue')),
      (api.Event.LINE_DELETE, api.Line('  # \'my-app                   == x.x.x\',')),
      (api.Event.LINE_ADD, api.Line('  \'my-app                   == 1.2.3\',')),
      (api.Event.LINE_SAME, api.Line('  \'APScheduler              == 2.1.0\',')),
      (api.Event.LINE_SAME, api.Line('  \'kombu                    == 2.5.10\',')),
      (api.Event.LINE_SAME, api.Line('  \'amqp                     == 1.0.11\',')),
      (api.Event.ENTRY_END, ent2),
      (api.Event.ENTRY_START, ent3),
      (api.Event.LINE_LOC, api.Line('@@ -68,4 +68,5 @@')),
      (api.Event.LINE_SAME, api.Line('https://pypi.python.org/packages/source/G/GeoAlchemy2/GeoAlchemy2-0.2.tar.gz#md5=14d73d09cdc47e3ed92e804883e61218')),
      (api.Event.LINE_SAME, api.Line('https://pypi.python.org/packages/source/t/transaction/transaction-1.4.1.zip#md5=8db2680bc0f999219861a67b8f335a88')),
      (api.Event.LINE_SAME, api.Line('https://pypi.python.org/packages/source/p/psycopg2/psycopg2-2.5.tar.gz#md5=facd82faa067e99b80146a0ee2f842f6')),
      (api.Event.LINE_DELETE, api.Line('https://pypi.python.org/packages/source/p/pyramid/pyramid-1.4.1.tar.gz#md5=044d42f609d567d7db2948a03fffcf7c')),
      (api.Event.LINE_NOTE, api.Line('\ No newline at end of file')),
      (api.Event.LINE_ADD, api.Line('https://pypi.python.org/packages/source/p/pyramid/pyramid-1.4.1.tar.gz#md5=044d42f609d567d7db2948a03fffcf7c')),
      (api.Event.LINE_ADD, api.Line('https://pypi.python.org/packages/source/m/my_app/my_app-1.2.3.tar.gz')),
      (api.Event.LINE_NOTE, api.Line('\ No newline at end of file')),
      (api.Event.ENTRY_END, ent3),
      (api.Event.ENTRY_START, ent4),
      (api.Event.LINE_NOTE, api.Line('(Binary files differ)')),
      (api.Event.ENTRY_END, ent4),
      (api.Event.ENTRY_START, ent5),
      (api.Event.PROPENTRY, api.PropertyEntry('Added: svn:mime-type', None, 'application/octet-stream')),
      (api.Event.ENTRY_END, ent5),
      (api.Event.PATCH_END, patch),
      ]

    data = asset.load('parsedifflib:data/svnlook.diff').read()
    gen = parsedifflib.parse_svnlook(data)
    chk = [(type, repr(obj)) for type, obj in chk]
    out = [(type, repr(obj)) for type, obj in gen]
    self.assertEqual(out, chk)

  #----------------------------------------------------------------------------
  def test_lineNumbers(self):
    src   = self.nietzsche_diff
    patch = api.Patch()
    entry = api.Entry(
      api.Entry.TYPE_CONTENT,
      'Quotes/FriedrichNietzsche-TheWay.txt',
      'Quotes/FriedrichNietzsche-TheWay.txt',
      '1844-10-15 00:00:00 UTC (rev 1)',
      '1900-08-25 00:00:00 UTC (rev 2)',
      'Modified: Quotes/FriedrichNietzsche-TheWay.txt')
    chk = [
      (api.Event.PATCH_START, patch),
      (api.Event.ENTRY_START, entry),
      (api.Event.LINE_LOC, api.Line('@@ -1,7 +1,7 @@')),
      (api.Event.LINE_SAME, api.Line('You have your way. I have my', oldnum=1, newnum=1)),
      (api.Event.LINE_SAME, api.Line('way. As for the right way, the', oldnum=2, newnum=2)),
      (api.Event.LINE_SAME, api.Line('correct way, and the only way,', oldnum=3, newnum=3)),
      (api.Event.LINE_DELETE, api.Line('it does not exist.', oldnum=4)),
      (api.Event.LINE_ADD, api.Line('it\'s definitely not your way ;).', newnum=4)),
      (api.Event.LINE_SAME, api.Line('', oldnum=5, newnum=5)),
      (api.Event.LINE_SAME, api.Line('  -- Friedrich Nietzsche', oldnum=6, newnum=6)),
      (api.Event.LINE_SAME, api.Line('     1844 - 1900', oldnum=7, newnum=7)),
      (api.Event.ENTRY_END, entry),
      (api.Event.PATCH_END, patch),
      ]
    gen = parsedifflib.parse_svnlook(src, {'lineNumbers': True})
    chk = [(type, repr(obj)) for type, obj in chk]
    out = [(type, repr(obj)) for type, obj in gen]
    self.assertEqual(out, chk)

  #----------------------------------------------------------------------------
  def test_lineNumbers_singleLine(self):
    src = '''\
Modified: content/textfile.txt
===================================================================
--- content/textfile.txt	2011-04-29 02:40:55 UTC (rev 2)
+++ content/textfile.txt	2011-04-29 02:57:23 UTC (rev 3)
@@ -1 +1 @@
-this is a sample textfile.txt.
+this is a sample textfile.txt with changes.
'''
    patch = api.Patch()
    entry = api.Entry(
      api.Entry.TYPE_CONTENT,
      'content/textfile.txt', 'content/textfile.txt',
      '2011-04-29 02:40:55 UTC (rev 2)',
      '2011-04-29 02:57:23 UTC (rev 3)',
      'Modified: content/textfile.txt')
    chk = [
      (api.Event.PATCH_START, patch),
      (api.Event.ENTRY_START, entry),
      (api.Event.LINE_LOC, api.Line('@@ -1 +1 @@')),
      (api.Event.LINE_DELETE, api.Line('this is a sample textfile.txt.', oldnum=1)),
      (api.Event.LINE_ADD, api.Line('this is a sample textfile.txt with changes.', newnum=1)),
      (api.Event.ENTRY_END, entry),
      (api.Event.PATCH_END, patch),
      ]
    gen = parsedifflib.parse_svnlook(src, {'lineNumbers': True})
    chk = [(type, repr(obj)) for type, obj in chk]
    out = [(type, repr(obj)) for type, obj in gen]
    self.assertEqual(out, chk)

  #----------------------------------------------------------------------------
  def test_intraLineDiff(self):
    src   = self.nietzsche_diff
    patch = api.Patch()
    entry = api.Entry(
      api.Entry.TYPE_CONTENT,
      'Quotes/FriedrichNietzsche-TheWay.txt',
      'Quotes/FriedrichNietzsche-TheWay.txt',
      '1844-10-15 00:00:00 UTC (rev 1)',
      '1900-08-25 00:00:00 UTC (rev 2)',
      'Modified: Quotes/FriedrichNietzsche-TheWay.txt')
    chk = [
      (api.Event.PATCH_START, patch),
      (api.Event.ENTRY_START, entry),
      (api.Event.LINE_LOC, api.Line('@@ -1,7 +1,7 @@')),
      (api.Event.LINE_SAME, api.Line('You have your way. I have my', oldnum=1, newnum=1)),
      (api.Event.LINE_SAME, api.Line('way. As for the right way, the', oldnum=2, newnum=2)),
      (api.Event.LINE_SAME, api.Line('correct way, and the only way,', oldnum=3, newnum=3)),
      (api.Event.LINE_DELETE, api.Line('it does not exist.', oldnum=4, segments=[
        (api.Event.SEGMENT_SAME, 'it d'),
        (api.Event.SEGMENT_DELETE, 'o'),
        (api.Event.SEGMENT_SAME, 'e'),
        (api.Event.SEGMENT_DELETE, 's'),
        (api.Event.SEGMENT_SAME, ' not '),
        (api.Event.SEGMENT_DELETE, 'exist'),
        (api.Event.SEGMENT_SAME, '.'),
        ])),
      (api.Event.LINE_ADD, api.Line('it\'s definitely not your way ;).', newnum=4, segments=[
        (api.Event.SEGMENT_SAME, 'it'),
        (api.Event.SEGMENT_ADD, '\'s'),
        (api.Event.SEGMENT_SAME, ' de'),
        (api.Event.SEGMENT_ADD, 'finitely'),
        (api.Event.SEGMENT_SAME, ' not '),
        (api.Event.SEGMENT_ADD, 'your way ;)'),
        (api.Event.SEGMENT_SAME, '.'),
        ])),
      (api.Event.LINE_SAME, api.Line('', oldnum=5, newnum=5)),
      (api.Event.LINE_SAME, api.Line('  -- Friedrich Nietzsche', oldnum=6, newnum=6)),
      (api.Event.LINE_SAME, api.Line('     1844 - 1900', oldnum=7, newnum=7)),
      (api.Event.ENTRY_END, entry),
      (api.Event.PATCH_END, patch),
      ]
    gen = parsedifflib.parse_svnlook(src, {'lineNumbers': True, 'intraLineDiff': True})
    chk = [(type, repr(obj)) for type, obj in chk]
    out = [(type, repr(obj)) for type, obj in gen]
    self.assertEqual(out, chk)

  #----------------------------------------------------------------------------
  def test_intraLineDiff_singleLine(self):
    src = '''\
Modified: content/textfile.txt
===================================================================
--- content/textfile.txt	2011-04-29 02:40:55 UTC (rev 2)
+++ content/textfile.txt	2011-04-29 02:57:23 UTC (rev 3)
@@ -1 +1 @@
-this is a sample textfile.txt.
+this is a sample textfile.txt with changes.
'''
    patch = api.Patch()
    entry = api.Entry(
      api.Entry.TYPE_CONTENT,
      'content/textfile.txt', 'content/textfile.txt',
      '2011-04-29 02:40:55 UTC (rev 2)',
      '2011-04-29 02:57:23 UTC (rev 3)',
      'Modified: content/textfile.txt')
    chk = [
      (api.Event.PATCH_START, patch),
      (api.Event.ENTRY_START, entry),
      (api.Event.LINE_LOC, api.Line('@@ -1 +1 @@')),
      (api.Event.LINE_DELETE, api.Line('this is a sample textfile.txt.', oldnum=1, segments=[
         (api.Event.SEGMENT_SAME, 'this is a sample textfile.txt.'),
         ])),
      (api.Event.LINE_ADD, api.Line('this is a sample textfile.txt with changes.', newnum=1, segments=[
         (api.Event.SEGMENT_SAME, 'this is a sample textfile.txt'),
         (api.Event.SEGMENT_ADD, ' with changes'),
         (api.Event.SEGMENT_SAME, '.'),
         ])),
      (api.Event.ENTRY_END, entry),
      (api.Event.PATCH_END, patch),
      ]
    gen = parsedifflib.parse_svnlook(src, {'lineNumbers': True, 'intraLineDiff': True})
    chk = [(type, repr(obj)) for type, obj in chk]
    out = [(type, repr(obj)) for type, obj in gen]
    self.assertEqual(out, chk)

  #----------------------------------------------------------------------------
  def test_property_default(self):
    src = self.propEntry_diff
    patch = api.Patch()
    entry = api.Entry(
      api.Entry.TYPE_PROPERTY,
      None, None, None, None,
      'Property changes on: property/file1.txt')
    propent = api.PropertyEntry(
      'Modified: test:property1',
      old = 'one line\n\n(blank line above and below too)\n\n',
      new = 'one line\n(blank line above removed)\n(blank line below)\n\n')
    chk = [
      (api.Event.PATCH_START, patch),
      (api.Event.ENTRY_START, entry),
      (api.Event.PROPENTRY, propent),
      (api.Event.ENTRY_END, entry),
      (api.Event.PATCH_END, patch),
      ]
    gen = parsedifflib.parse_svnlook(src)
    chk = [(type, repr(obj)) for type, obj in chk]
    out = [(type, repr(obj)) for type, obj in gen]
    self.assertEqual(out, chk)

  #----------------------------------------------------------------------------
  def test_property_propertyUnifiedDiff(self):
    src = self.propEntry_diff
    patch = api.Patch()
    entry = api.Entry(
      api.Entry.TYPE_PROPERTY,
      None, None, None, None,
      'Property changes on: property/file1.txt')
    propent = api.PropertyEntry(
      'Modified: test:property1',
      old = 'one line\n\n(blank line above and below too)\n\n',
      new = 'one line\n(blank line above removed)\n(blank line below)\n\n')
    chk = [
      (api.Event.PATCH_START, patch),
      (api.Event.ENTRY_START, entry),
      (api.Event.PROPENTRY_START, propent),
      (api.Event.LINE_LOC, api.Line('@@ -1,5 +1,5 @@')),
      (api.Event.LINE_SAME, api.Line('one line')),
      (api.Event.LINE_DELETE, api.Line('')),
      (api.Event.LINE_DELETE, api.Line('(blank line above and below too)')),
      (api.Event.LINE_ADD, api.Line('(blank line above removed)')),
      (api.Event.LINE_ADD, api.Line('(blank line below)')),
      (api.Event.LINE_SAME, api.Line('')),
      (api.Event.LINE_SAME, api.Line('')),
      (api.Event.PROPENTRY_END, propent),
      (api.Event.ENTRY_END, entry),
      (api.Event.PATCH_END, patch),
      ]
    gen = parsedifflib.parse_svnlook(src, {'propertyUnifiedDiff': True})
    chk = [(type, repr(obj)) for type, obj in chk]
    out = [(type, repr(obj)) for type, obj in gen]
    self.assertEqual(out, chk)

  #----------------------------------------------------------------------------
  def test_property_propertyUnifiedDiff_lineNumbers(self):
    src = self.propEntry_diff
    patch = api.Patch()
    entry = api.Entry(
      api.Entry.TYPE_PROPERTY,
      None, None, None, None,
      'Property changes on: property/file1.txt')
    propent = api.PropertyEntry(
      'Modified: test:property1',
      old = 'one line\n\n(blank line above and below too)\n\n',
      new = 'one line\n(blank line above removed)\n(blank line below)\n\n')
    chk = [
      (api.Event.PATCH_START, patch),
      (api.Event.ENTRY_START, entry),
      (api.Event.PROPENTRY_START, propent),
      (api.Event.LINE_LOC, api.Line('@@ -1,5 +1,5 @@')),
      (api.Event.LINE_SAME, api.Line('one line', oldnum=1, newnum=1)),
      (api.Event.LINE_DELETE, api.Line('', oldnum=2)),
      (api.Event.LINE_DELETE, api.Line('(blank line above and below too)', oldnum=3)),
      (api.Event.LINE_ADD, api.Line('(blank line above removed)', newnum=2)),
      (api.Event.LINE_ADD, api.Line('(blank line below)', newnum=3)),
      (api.Event.LINE_SAME, api.Line('', oldnum=4, newnum=4)),
      (api.Event.LINE_SAME, api.Line('', oldnum=5, newnum=5)),
      (api.Event.PROPENTRY_END, propent),
      (api.Event.ENTRY_END, entry),
      (api.Event.PATCH_END, patch),
      ]
    gen = parsedifflib.parse_svnlook(src, {
      'lineNumbers': True, 'propertyUnifiedDiff': True})
    chk = [(type, repr(obj)) for type, obj in chk]
    out = [(type, repr(obj)) for type, obj in gen]
    self.assertEqual(out, chk)

  #----------------------------------------------------------------------------
  def runtest(self, item):
    out = colorize(asset.load('parsedifflib:' + item.name).read())
    chk = asset.load('parsedifflib:' + item.name + '.output.reference').read()
    self.assertMultiLineEqual(out, chk)

for item in asset.load('parsedifflib:data/*.diff'):
  safename = re.sub('[^a-zA-Z0-9]+', '_', item.name[5:-5])
  def make_test(item):
    def test_asset(self):
      self.runtest(item)
    return test_asset
  setattr(TestParseDiffLib, 'test_auto_' + safename, make_test(item))

#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------
