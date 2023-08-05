#!/usr/bin/env python

# $Id: fitsdiff.py 16870 2012-05-18 13:52:53Z embray $

"""fitsdiff is now a part of PyFITS--the fitsdiff in PyFITS replaces the
fitsdiff that used to be in the module.

Now this module just provides a wrapper around pyfits.diff for backwards
compatibility with the old interface in case anyone uses it.
"""

import os
import sys


from pyfits.diff import FITSDiff
from pyfits.scripts.fitsdiff import log, main


def fitsdiff(input1, input2, comment_excl_list='', value_excl_list='',
             field_excl_list='', maxdiff=10, delta=0.0, neglect_blanks=True,
             output=None):

    if isinstance(comment_excl_list, basestring):
        comment_excl_list = list_parse(comment_excl_list)

    if isinstance(value_excl_list, basestring):
        value_excl_list = list_parse(value_excl_list)

    if isinstance(field_excl_list, basestring):
        field_excl_list = list_parse(field_excl_list)

    diff = FITSDiff(input1, input2, ignore_keywords=value_excl_list,
                    ignore_comments=comment_excl_list,
                    ignore_fields=field_excl_list, numdiffs=maxdiff,
                    tolerance=delta, ignore_blanks=neglect_blanks)

    if output is None:
        output = sys.stdout

    diff.report(output)

    return diff.identical


def list_parse(name_list):
    """Parse a comma-separated list of values, or a filename (starting with @)
    containing a list value on each line.
    """

    if name_list and name_list[0] == '@':
        value = name_list[1:]
        if not os.path.exists(value):
            log.warning('The file %s does not exist' % value)
            return
        try:
            return [v.strip() for v in open(value, 'r').readlines()]
        except IOError, e:
            log.warning('reading %s failed: %s; ignoring this file' %
                        (value, e))
    else:
        return [v.strip() for v in name_list.split(',')]


if __name__ == "__main__":
    sys.exit(main())
