#-*- coding: utf-8 -*-
#
# Copyright © 2014 Jean des Morts <jean.des.morts@gmail.com>
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To Public License, Version 2,
# as published by Sam Hocevar. See the COPYING.WTFPL file for more details.

__author__ = 'jdmorts'

from collections import namedtuple
from collections import deque


def remove_col_wrap(column_spec, column_names, rows):
    """Given a set of rows and column widths, concatentate the fields of each
    column until the number of fields equals the number of columns. If two rows
    each contain five fields in five columns, this function returns one row of
    five fields in five columns. Any leading/trailing spaces are removed.

    This::

       a    b         c  d e
     ['----|---------|--|-|----------',
      ' ---|  -------|--|-| -----------']

    becomes::

     {'a': '-------',
      'b': '-------',
      'c': '----------------',
      'd': '----',
      'e': '--',
      'f': '---------------------'}

    :param column_spec: row widths stored as int
    :type column_spec: list of int
    :param column_names: used as keys to build record dict
    :type column_names: list of str
    :param rows: rows of a column-wrapped record
    """
    record = {}
    offset = 0

    for col_width, col_name in zip(column_spec, column_names):
        column = ''
        # Strip line ends and left justify so len(row) == sum(column_spec)
        for row in (r.rstrip('\n\r').ljust(sum(column_spec)) for r in rows):
            # Concatenate lines in the current column
            col_slice = slice(offset, offset + col_width)
            column += row[col_slice].strip()
        # Add column to record and set offset for next column
        record[col_name] = column
        offset += col_width + 1

    return record


def parse_show(output, class_name, repr_method=None):
    """Parse Dell EqualLogic 'show' command output. While the formatting is
    consistent, it's tricksy on account of an ill-conceived column wrap. The
    following is sample output illustrating this curious 'feature'::

        EQGroup01> volume select MBX01-DB01 access show
        ID  Initiator                     Ipaddress       AuthMethod UserName   Apply-To
        --- ----------------------------- --------------- ---------- ---------- --------
        1   iqn.1998-01.com.vmware:xxxxxv *.*.*.*         none                  volume
              m01-4c08cb5e
        2   iqn.1998-01.com.vmware:xxxxxv *.*.*.*         none                  volume
              m02-7b27a2a8
        . . .

    Because the use of hyphens to denote column width is consistent, we can
    precisely specify the number of characters in each column using the
    number of hyphens observed. Also, notice the two-space indent where the
    'Initiator' column wraps; this must be stripped before concatenation.

    :param output: output from an EqualLogic CLI 'show' command
    :type output: list of str
    :param class_name: type given to the namedtuples to create for each record
    :type class_name: str
    :param repr_method: function given to __repr__ for all namedtuples returned
    :type repr_method: function
    """
    col_spec = []  # Column slices
    col_names = []  # Column headers
    Klass = None  # Container class
    last_line = ''  # Used to catch column headers once we see hypens
    saw_prompt = False
    records = {}

    try:
        lines = deque(output)

    except TypeError:
        raise TypeError('Unexpected output type {:s}'.format(type(output)))

    while True:
        try:
            cur_line = lines.popleft().rstrip('\n')

            if not cur_line:
                continue

        except IndexError:
            break

        # Identify EQ prompts; ignore remaining output if we see two of them
        if cur_line.split(' ', 1)[0].endswith('>'):
            if saw_prompt:
                break
            else:
                saw_prompt = True
        # Store column headers and hyphens for column widths. Sanitize column
        # names. Give the output class a proper __repr__
        elif cur_line.startswith('-'):
            col_spec = [len(c) for c in cur_line.split()]
            col_names = [col.lower()
                         for col in last_line.replace('-', '_').split()]

            Klass = namedtuple(class_name, col_names)
            if repr_method:
                Klass.__repr__ = repr_method
        # Once we know the column widths,
        elif col_spec:
            rows = [cur_line]
            # Gather continuing lines resulting from column wrap
            while True:
                try:
                    # If next line is a continuation of current line,
                    if lines[0].startswith(' '):
                        rows.append(lines.popleft())
                    else:
                        break

                except IndexError:
                    break
            # Combine like columns in rows of the same record
            record = remove_col_wrap(col_spec, col_names, rows)
            # Store record in container object and use first column as dict key
            obj = Klass(**record)
            key = record[col_names[0]]
            records[key] = obj
        # Update last_line to current line
        last_line = cur_line

    return records
