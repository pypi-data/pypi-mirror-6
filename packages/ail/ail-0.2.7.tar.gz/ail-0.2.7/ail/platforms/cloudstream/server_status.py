#-*- coding: utf-8 -*-
#
# Copyright © 2014 Jean des Morts <jean.des.morts@gmail.com>
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To Public License, Version 2,
# as published by Sam Hocevar. See the COPYING.WTFPL file for more details.

__author__ = 'jdmorts'

from ail import Profile
from ail.services.ssh import SSHService


class ServerStatus(object):
    """
    """
    def __init__(self, output):
        try:
            self._pid = output[0].split(': ')[1]
            self._status = 'running'

        except IndexError:
            self._pid = 0

            if output:
                self._status = 'stopped'
            else:
                self._status = 'unknown'

    @property
    def pid(self):
        return self._pid

    @property
    def status(self):
        return self._status


class SSHProfile(Profile):
    """
    """
    service = SSHService

    @property
    def _input(self):
        return "./server status",

    @staticmethod
    def _parse(output):
        return ServerStatus(output)
