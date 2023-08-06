#-*- coding: utf-8 -*-
#
# Copyright © 2014 Jean des Morts <jean.des.morts@gmail.com>
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To Public License, Version 2,
# as published by Sam Hocevar. See the COPYING.WTFPL file for more details.

__author__ = 'jdmorts'

from ail import Profile
from ail.services.ssh import SSHService


class SSHDPermitRoot(object):
    """
    """
    def __init__(self, output):
        self._sshd_permit_root = None

        try:
            line = output[0]
            # If we successfully read the sshd_config file
            if 'error' not in line:
                try:
                    value = line.split()[1].lower()

                except IndexError:
                    # In case PermitRootLogin is not set
                    value = ''
                # If PermitRootLogin is set to 'no'
                if value == 'no':
                    self._sshd_permit_root = False
                # Otherwise, if it's set to 'yes', or simply not set
                else:
                    self._sshd_permit_root = True

        except IndexError:
            # Pass if we failed to obtain output
            pass

    @property
    def sshd_permit_root(self):
        if self._sshd_permit_root is None:
            return 'unknown'
        else:
            return str(self._sshd_permit_root).lower()

    def to_xml(self, empty=False, indent=0, tag='sshd_permit_root'):
        spaces = ' ' * indent
        xml = spaces + ('<sshd_permit_root>{}</sshd_permit_root>\n'.
                        format(self.sshd_permit_root))

        return xml


class SSHProfile(Profile):
    """
    """
    service = SSHService

    @property
    def _input(self):
        return ("cat /etc/ssh/sshd_config 2>/dev/null || echo error" +
                "| egrep -i '^[^#]*permitrootlogin'",)

    @staticmethod
    def _parse(output):
        return SSHDPermitRoot(output)
