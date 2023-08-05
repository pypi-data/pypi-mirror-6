# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id$
# auth: metagriffin <mg.github@metagriffin.net>
# date: 2013/12/27
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

import sys
import argparse
import json
from gettext import gettext
import parsedifflib

#------------------------------------------------------------------------------
def _(message, *args, **kw):
  if args or kw:
    return gettext(message).format(*args, **kw)
  return gettext(message)

#------------------------------------------------------------------------------
def main(argv=None):

  cli = argparse.ArgumentParser(
    description=_('Reports the parsedifflib tokens found when provided'
                  ' a file (this is mostly a development/debugging tool.'))

  cli.add_argument(
    _('-s'), _('--setting'), metavar=_('NAME=VALUE'),
    dest='settings', default=[], action='append',
    help=_('specify a parsedifflib setting; note that the "VALUE" is'
           ' expected to be JSON-encoded'))

  cli.add_argument(
    'filename', metavar=_('FILENAME'),
    nargs='?',
    help=_('filename to parse; if not specified or "-", STDIN'
           ' is used instead'))

  options = cli.parse_args(argv)

  if not options.filename or options.filename == '-':
    options.filename = sys.stdin
  else:
    options.filename = open(options.filename, 'rb')

  options.settings = dict([
    (setting.split('=', 1)[0], json.loads(setting.split('=', 1)[1]))
    for setting in options.settings])

  for etype, obj in parsedifflib.parse_svnlook(options.filename, options.settings):
    for attr in dir(parsedifflib.Event):
      if getattr(parsedifflib.Event, attr) is etype:
        etype = attr
        break
    else:
      etype = 'UNKNOWN[{!r}]'.format(etype)
    print etype,repr(obj)

#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------
