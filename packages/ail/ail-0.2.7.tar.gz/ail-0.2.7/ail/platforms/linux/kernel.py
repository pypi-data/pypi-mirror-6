#-*- coding: utf-8 -*-
#
# Copyright © 2014 Jean des Morts <jean.des.morts@gmail.com>
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To Public License, Version 2,
# as published by Sam Hocevar. See the COPYING.WTFPL file for more details.

__author__ = 'jdmorts'

import logging

from ail import Profile
from ail.services.ssh import SSHService
from ail.util import make_to_xml

logger = logging.getLogger(__name__)


class Kernel(object):
    """Expected output:
    ::
     Linux 2.6.18-194.32.1.el5 #1 SMP Wed Jan 5 17:52:25 EST 2011 x86_64 GNU/Linux
    """
    def __init__(self, output):
        self._arch = None
        self._name = None
        self._os = None
        self._release = None
        self._version = None
        self._to_xml = make_to_xml(('name', 'release', 'version', 'architecture'))

        try:
            self._name, self._release, vestige = output[0].split(None, 2)
            vestige, self._arch, self._os = vestige.rsplit(None, 2)
            self._version = vestige

        except (IndexError, TypeError, ValueError):
            raise ValueError('Unable to initialize Kernel object')

    @property
    def architecture(self):
        return self._arch

    @property
    def name(self):
        return self._name

    @property
    def operating_system(self):
        return self._os

    @property
    def release(self):
        return self._release

    @property
    def version(self):
        return self._version

    def to_xml(self, empty=True, indent=0):
        return self._to_xml(self, empty=empty, indent=indent)


class SSHProfile(Profile):
    """
    """
    service = SSHService

    @property
    def _input(self):
        return "uname -osrvm 2>/dev/null",

    @staticmethod
    def _parse(output):
        return Kernel(output)
