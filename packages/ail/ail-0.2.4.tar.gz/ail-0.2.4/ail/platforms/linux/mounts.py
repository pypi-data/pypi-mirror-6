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
from ail.util import make_to_xml, make_container

logger = logging.getLogger(__name__)

Mount = make_container('Mount', ('fs_spec', 'fs_file', 'fs_vfstype', 'fs_mntops'))


class Mounts(object):
    """Expected format:

    /dev/mapper/VolGroup00-LogVol00 on / type ext3 (rw)
    proc on /proc type proc (rw)
    sysfs on /sys type sysfs (rw)
    devpts on /dev/pts type devpts (rw,gid=5,mode=620)
    /dev/hda1 on /boot type ext3 (rw)
    tmpfs on /dev/shm type tmpfs (rw)
    none on /proc/sys/fs/binfmt_misc type binfmt_misc (rw)
    //10.0.5.190/XMLImport on /mnt/winmnt type cifs (rw,mand)
    """
    def __init__(self, output):
        self._mounts = []
        self._to_xml = make_to_xml(())

        try:
            for record in (l.strip().split() for l in output):
                fs_mntops = record[5].strip('()')
                self._mounts.append(Mount(*(record[:5:2] + [fs_mntops])))

        except (IndexError, ValueError):
            # If not enough fields in record,
            raise ValueError('Unable to initialize Mounts object')

    def __iter__(self):
        for mount in self._mounts:
            yield mount

    def to_xml(self, empty=False, indent=0):
        return self._to_xml(self, [m for m in self], indent=indent)


class SSHProfile(Profile):
    """"""

    service = SSHService

    @property
    def _input(self):
        return "mount 2>/dev/null",

    @staticmethod
    def _parse(output):
        return Mounts(output)
