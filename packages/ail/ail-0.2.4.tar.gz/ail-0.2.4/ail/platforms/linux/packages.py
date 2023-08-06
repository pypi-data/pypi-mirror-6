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

Package = make_container('Package', ('package', 'version'))


class Packages(object):
    """Example output:
    ::
        GConf2.i386 2.14.0-9.el5
        GConf2.x86_64 2.14.0-9.el5
        GConf2-devel.x86_64 2.14.0-9.el5
        ImageMagick.i386
        ImageMagick.x86_64 6.2.8.0-15.el5_8
    """
    def __init__(self, output):
        self._packages = []
        self._to_xml = make_to_xml(())

        for record in (l.strip().split() for l in output):
            try:
                self._packages.append(Package(*record))

            except ValueError:
                # If not enough fields in record,
                try:
                    self._packages.append(Package(record[0], ''))

                except IndexError:
                    logger.warn('Unable to parse package {:s}'.
                                format(str(record)))

    def __iter__(self):
        for package in self._packages:
            yield package

    def to_xml(self, empty=False, indent=0):
        return self._to_xml(self, [u for u in self], indent=indent)


class SSHProfile(Profile):
    """
    """
    service = SSHService

    @property
    def _input(self):
        return ("yum list installed 2>/dev/null | tail -n +3 | " +
                "awk '{print $1,$2}'",)

    @staticmethod
    def _parse(output):
        return Packages(output)
