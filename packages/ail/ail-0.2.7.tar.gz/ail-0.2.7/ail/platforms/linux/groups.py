#-*- coding: utf-8 -*-
#
# Copyright © 2014 Jean des Morts <jean.des.morts@gmail.com>
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To Public License, Version 2,
# as published by Sam Hocevar. See the COPYING.WTFPL file for more details.

__author__ = 'jdmorts'

from collections import namedtuple
import logging

from ail import Profile
from ail.services.ssh import SSHService
from ail.util import make_to_xml, make_container

logger = logging.getLogger(__name__)

group_attrs = ('group_name', 'password', 'gid', 'users')
Group = namedtuple('Group', group_attrs)
Group.to_xml = make_to_xml(group_attrs[:3])

User = make_container('User', ('username',))


class Groups(object):
    """"""

    def __init__(self, output):
        self._groups = {}

        for record in (l.strip().split(':') for l in output):
            try:
                group = Group(*(record[:3] +
                                [[User(u) for u in record[3].split(',')
                                  if u]]))

                self._groups[record[0]] = group

            except (IndexError, ValueError):
                # If not enough fields in record,
                logger.warn('Unable to parse group {:s}'.format(record))

    def __iter__(self):
        for name in sorted(self._groups.keys()):
            yield self._groups[name]

    def group(self, group):
        try:
            return self._groups[group]

        except KeyError:
            # If no key exists for group,
            raise LookupError('Unknown group {:s}'.format(group))

        except TypeError:
            # If group is not hashable,
            raise TypeError('Invalid group type {:s}'.format(type(group)))

    def to_xml(self, empty=False, indent=0):
        # TODO: work out a better way to handle these many-depth recursions
        spaces = (' ' * indent)
        xml = spaces + '<groups>\n'

        for group in self:
            xml = ''.join((xml, group.to_xml(group.users, indent=(indent + 2))))

        xml = ''.join((xml, spaces + '</groups>\n'))

        return xml


class SSHProfile(Profile):
    """"""

    service = SSHService

    @property
    def _input(self):
        return "cat /etc/group 2>/dev/null",

    @staticmethod
    def _parse(output):
        return Groups(output)
