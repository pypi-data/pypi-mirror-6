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

logger = logging.getLogger(__name__)


class Distribution(object):
    """
    """
    def __init__(self, output):
        self._issue = ''

        try:
            for record in (l.split('=') for l in output):
                if len(record) == 2:
                    if record[0].startswith('PRETTY'):
                        self._distribution = record[1].strip('"')
                        break
                else:
                    self._distribution = record[0]

        except IndexError:
            raise ValueError('Unable to initialize Distribution object')

    @property
    def distribution(self):
        return self._distribution

    def to_xml(self, empty=False, indent=0):
        spaces = ' ' * indent
        xml = (spaces +
               "<distribution>{}</distribution>\n".format(self._distribution))

        return xml


class SSHProfile(Profile):
    """"""

    service = SSHService

    @property
    def _input(self):
        return "cat /etc/*-release 2>/dev/null",

    @staticmethod
    def _parse(output):
        return Distribution(output)
