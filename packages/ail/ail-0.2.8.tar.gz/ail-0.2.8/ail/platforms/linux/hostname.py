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


class Hostname(object):
    """
    """
    def __init__(self, output):
        try:
            self._hostname = '.'.join(output[0].split(' ', 1))

        except IndexError:
            logger.warn('Unable to parse hostname {:s}'.format(output))
            self._hostname = ''

    def to_xml(self, empty=False, indent=0):
        spaces = ' ' * indent

        return spaces + '<hostname>{}</hostname>\n'.format(self._hostname)


class SSHProfile(Profile):
    """
    """
    service = SSHService

    @property
    def _input(self):
        return "echo `hostname -s 2>/dev/null` `hostname -d 2>/dev/null`",

    @staticmethod
    def _parse(output):
        return Hostname(output)
