#-*- coding: utf-8 -*-
#
# Copyright © 2014 Jean des Morts <jean.des.morts@gmail.com>
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To Public License, Version 2,
# as published by Sam Hocevar. See the COPYING.WTFPL file for more details.

__author__ = 'jdmorts'

from ail.platforms.equallogic.parse_show import parse_show


def volumeace_repr(self):
    """Do the opposite of parse_show, wrapping columns onto additional rows.
    This function is given to parse_show as the replacement for __repr__ on all
    returned objects, giving us an easy means to invert the parse_show
    operation.
    """
    header = """
ID  Initiator                     Ipaddress       AuthMethod UserName   Apply-To
--- ----------------------------- --------------- ---------- ---------- --------
"""
    # Obtain the column names and make suitable for use as field names
    col_names = [c.lower().replace('-', '_')
                 for c in header.splitlines()[1].split()]
    # Obtain the column widths
    col_spec = [len(c) for c in header.splitlines()[2].split()]
    rows = []
    # Store current offset for each column, by column name
    offsets = dict(zip(col_names, [0] * len(col_spec)))

    for i in range(4):
        row = []
        indent = ''

        for col_width, col_name in zip(col_spec, col_names):
            offset = offsets[col_name]
            field = getattr(self, col_name)
            # Make room for a two space indent in the middle of wrapped fields
            if offset > 0:
                indent = '  '
                col_width -= 2
            # If we have enough field to fill a column, grab a column's worth
            if offset + col_width <= len(field):
                field_slice = slice(offset, offset + col_width)
            # Barring that, grab whatever is left
            elif offset <= len(field):
                field_slice = slice(offset, len(field))
            # If nothing is left to grab, take an empty slice
            else:
                field_slice = slice(len(field), len(field))
            # Add any indent and left-justify our new field to fill the column
            row += [indent + field[field_slice].ljust(col_width)]
            offsets[col_name] += col_width  # Update the field offset

        # Terminate when we run out of field data
        if [''] * len(col_spec) == [r.strip() for r in row]:
            break
        # Otherwise, add our new row to the output
        else:
            rows.append(row)
    # Turn this mess of lists into a string
    return str('\n'.join([' '.join(row).rstrip() for row in rows]))


def test_parse_show():
    """Check consistency of parse_show/remove_col_wrap

    Given test output and some unrelated but plausible noise, parse the whole
    lot using a special __repr__ function to effectively undo all of
    parse_show's hard work. This permits us to compare the original value with
    the value produced after applying both our function and its inverse. These
    two values should be identical.

    As an added bonus, parse_show relies on remove_col_wrap, thus this function
    effectively tests remove_col_wrap, as well.
    """
    output = """EQGroup01> volume select VMSTORE10 access show
ID  Initiator                     Ipaddress       AuthMethod UserName   Apply-To
--- ----------------------------- --------------- ---------- ---------- --------
1   iqn.1998-01.com.vmware:xxxxxv *.*.*.*         none                  both
      m02-7b27a2a8
2   iqn.1998-01.com.vmware:xxxxxv *.*.*.*         none                  volume
      m01-4c08cb5e"""

    noise = """EQGroup01> volume show
Name            Size       Snapshots Status  Permission Connections TP
--------------- ---------- --------- ------- ---------- ----------- -
MBX02-DBPF      5GB        0         online  read-write 26          N
BlahBlah        1TB        0         online  read-write 1           N
"""
    # Parse the combined output and noise, returning a dict of Test objects
    records = parse_show(output.splitlines() + noise.splitlines(), 'Test',
                         volumeace_repr)

    # Obtaining the repr of each Test object...
    new_output = '\n'.join(output.splitlines()[0:3] +
                           [repr(r) for r in records.values()]).rstrip()
    # ...should return the original output. Cross your fingers.
    assert output == new_output
