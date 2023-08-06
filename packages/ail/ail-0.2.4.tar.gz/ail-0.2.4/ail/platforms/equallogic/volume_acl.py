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


def volumeace_repr(self):
    """Handles __repr__/__str__ output for the VolumeACE class.
    """
    try:
        return (('{{"id": {id}, "initiator": "{initiator}", "ipaddress": ' +
                 '"{ipaddress}", "authmethod": "{authmethod}", "username": ' +
                 '"{username}", "apply_to": "{apply_to}"}}').
                format(id=self.id, initiator=self.initiator,
                       ipaddress=self.ipaddress, authmethod=self.authmethod,
                       username=self.username, apply_to=self.apply_to))

    except AttributeError:
        return ''


class VolumeACE(object):
    """Taken from `<http://psonlinehelp.equallogic.com/V3.3/volume_select_access_create_.htm>`_:
    ::

        Format -
        volume select vol_name access create parameter ...

        Parameters -
        initiator <name>
        ipaddress <ip_address|*.*.*.*>
        authmethod <chap|none>
        username <chap_name>
        apply-to <volume|snapshot|both>
    """
    def __init__(self, id=None, initiator=None, ipaddress=None, authmethod=None,
                 username=None, apply_to=None):

        self._id = id
        self._initiator = initiator
        self._ipaddress = ipaddress
        self._authmethod = authmethod if authmethod in ('chap', 'none') else None
        self._username = username
        self._apply_to = apply_to if apply_to in ('volume', 'snapshot', 'both') else None

    def __repr__(self):
        """Output in EqualLogic CLI format, suitable for entering commands"""

        my_repr = ''
        args = ('_initiator', '_ipaddress', '_authmethod', '_username',
                '_apply_to')

        for arg in args:
            attr = getattr(self, arg)

            if attr:
                my_repr = ' '.join((my_repr, arg.strip('_'), attr))

        return my_repr.replace('_', '-')

    def __str__(self):
        """Output as JSON for convenience"""

        my_str = ''
        args = ('id', 'initiator', 'ipaddress', 'authmethod', 'username',
                'apply_to')

        for arg in args:
            attr = getattr(self, arg)
            my_str = ', '.join((my_str, '"{}": "{}"'.format(arg, attr)))

        return '{' + my_str + '}'

    @property
    def id(self):
        return self._id or ''

    @property
    def initiator(self):
        return self._initiator or ''

    @property
    def ipaddress(self):
        return self._ipaddress or '*.*.*.*'

    @property
    def authmethod(self):
        return self._authmethod or 'none'

    @property
    def username(self):
        return self._username or ''

    @property
    def apply_to(self):
        return self._apply_to or 'both'


class VolumeACL(object):
    """Parse EqualLogic output from 'volume select ... access show' and store the
    resulting data as a dict of Volume objects, each containing id, initiator,
    ipaddress, authmethod, username, and apply-to."""

    def __init__(self, output):
        self._acl = parse_show(output, 'VolumeACE', volumeace_repr)

    def __repr__(self):
        return 'VolumeACL({})'.format(len(self._acl))

    def __str__(self):
        return '\n'.join([str(ace) for ace in self])

    def __iter__(self):
        for ace_id in sorted(self._acl.keys(), key=int):
            yield self._acl[ace_id]


class TelnetProfile(Profile):
    """Retrieve volume access information via Telnet"""

    service = EqualLogicCLIService

    def __init__(self, volume_name):
        super(TelnetProfile, self).__init__()
        self._volume_name = volume_name

    @property
    def _input(self):
        return ("", "volume select {} access show".format(self._volume_name)),

    @staticmethod
    def _parse(output):
        return VolumeACL(output)
