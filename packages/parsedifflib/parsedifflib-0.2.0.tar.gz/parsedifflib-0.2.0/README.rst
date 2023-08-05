==========================
Diff Patch Parsing Library
==========================

The `parsedifflib` package parses any style of diff patch into an
event stream of patch instructions. These instructions can then be
applied, colorized, reformatted, dissected, analyzed, etc.

.. warning::

  2013/12/09: currently only the `svnlook` format and stream-oriented
  event output is supported. Eventually, all the formats supported by
  colordiff are intended to be supported as well as structured output.


Usage
=====

.. code-block:: python

  import parsedifflib, subprocess

  data = subprocess.check_output('svnlook diff /path/to/repos', shell=True)

  for event, target in parsedifflib.parse_svnlook(data, {'lineNumbers': True}):

    if event in ( parsedifflib.Event.PATCH_START,
                  parsedifflib.Event.PATCH_END,
                  parsedifflib.Event.ENTRY_END,
                  parsedifflib.Event.LINE_LOC,
                  parsedifflib.Event.LINE_SAME,
                  parsedifflib.Event.LINE_NOTE,
                  parsedifflib.Event.PROPENTRY,
                ):
      continue

    elif event == parsedifflib.Event.ENTRY_START:
      print target.comment

    elif event == parsedifflib.Event.LINE_DELETE:
      print '  - deleted line %d: %s' % (target.oldnum, target.line)

    elif event == parsedifflib.Event.LINE_DELETE:
      print '  + added line %d: %s' % (target.newnum, target.line)


Credits
=======

Much inspiration came from:

* https://github.com/ymattw/cdiff
* https://github.com/kimmel/colordiff
