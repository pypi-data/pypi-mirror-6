#-*- coding: utf-8 -*-
#
# Copyright © 2014 Jean des Morts <jean.des.morts@gmail.com>
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To Public License, Version 2,
# as published by Sam Hocevar. See the COPYING.WTFPL file for more details.

__author__ = 'jdmorts'

from ail import Profile
from ail.services.telnet import EqualLogicCLIService
from .volume_acl import VolumeACE


class TelnetProfile(Profile):
    """Create new volume ACE"""

    service = EqualLogicCLIService

    def __init__(self, volume_name, ace):
        super(TelnetProfile, self).__init__()
        self._volume_name = volume_name
        self._ace = ace

        if not isinstance(ace, VolumeACE):
            raise TypeError('Unexpected ace type {:s}; should be {:s}'.
                            format(type(ace), type(VolumeACE)))

    @property
    def _input(self):
        command = "volume select {} access create {}".format(self._volume_name,
                                                             repr(self._ace))

        return "", command

    @staticmethod
    def _parse(output):
        return None
