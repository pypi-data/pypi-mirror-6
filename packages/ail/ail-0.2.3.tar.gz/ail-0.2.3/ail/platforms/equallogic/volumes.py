#-*- coding: utf-8 -*-
#
# Copyright © 2014 Jean des Morts <jean.des.morts@gmail.com>
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To Public License, Version 2,
# as published by Sam Hocevar. See the COPYING.WTFPL file for more details.

__author__ = 'jdmorts'

from ail import Profile
from ail.services.telnet import EqualLogicCLIService
from .parse_show import parse_show


def volume_repr(self):
    """Handles __repr__/__str__ output for the Volume class"""

    try:
        return (('{{"name": "{name}", "size": "{size}", "snapshots": ' +
                 '{snapshots}, "status": "{status}", "permission": ' +
                 '"{permission}", "connections": {connections}, "tp": "{tp}"}}').
                format(name=self.name, size=self.size, snapshots=self.snapshots,
                       status=self.status, permission=self.permission,
                       connections=self.connections, tp=self.tp))

    except AttributeError:
        return ''


class Volumes(object):
    """Parse EqualLogic output from 'volume show' and store the resulting data as
    a dict of Volume objects, each containing name, size, snapshots, status,
    permission, connections, and TP."""

    def __init__(self, output):
        self._volumes = parse_show(output, 'Volume', volume_repr)

    def __repr__(self):
        return 'Volumes({})'.format(len(self._volumes))

    def __str__(self):
        return '\n'.join([str(volume) for volume in self])

    def __iter__(self):
        for vol_id in sorted(self._volumes.keys()):
            yield self._volumes[vol_id]

    def volume(self, name):
        """Return volume information given a known volume name.

        :param name: name as it appears in 'volume show' output
        :type name: str
        :return: volume object containing name, size, snapshots, status,
            permission, connections, and TP.
        :rtype: Volume()"""

        try:
            return self._volumes[name]

        except KeyError:
            raise LookupError('Unknown volume name {:s}'.format(name))

        except TypeError:
            raise TypeError('Invalid volume name type {:s}'.format(type(name)))


class TelnetProfile(Profile):
    """Retrieve volume information via Telnet"""

    service = EqualLogicCLIService

    def __init__(self):
        super(TelnetProfile, self).__init__()

    @property
    def _input(self):
        return ("", "volume show"),

    @staticmethod
    def _parse(output):
        return Volumes(output)
