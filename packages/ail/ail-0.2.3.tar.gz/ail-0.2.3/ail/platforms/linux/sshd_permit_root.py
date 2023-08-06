#-*- coding: utf-8 -*-
#
# Copyright © 2014 Jean des Morts <jean.des.morts@gmail.com>
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To Public License, Version 2,
# as published by Sam Hocevar. See the COPYING.WTFPL file for more details.

__author__ = 'jdmorts'

from ail import Profile
from ail.services.ssh import SSHService
from ail.util import make_to_xml


class SSHDPermitRoot(object):
    """"""

    def __init__(self, output):
        self._sshd_permit_root = True
        self._to_xml = make_to_xml(('sshd_permit_root',))

        try:
            if output[0]:
                self._sshd_permit_root = False

        except IndexError:
            pass

    @property
    def sshd_permit_root(self):
        return str(self._sshd_permit_root).lower()

    def to_xml(self, empty=False, indent=0):
        spaces = ' ' * indent
        xml = spaces + ('<sshd_permit_root>{}</sshd_permit_root>\n'.
                        format(self._sshd_permit_root))

        return xml


class SSHProfile(Profile):
    """"""

    service = SSHService

    @property
    def _input(self):
        return ("cat /etc/ssh/sshd_config 2>/dev/null | " +
                "egrep -i '^[^#]*permitrootlogin'",)

    @staticmethod
    def _parse(output):
        return SSHDPermitRoot(output)
