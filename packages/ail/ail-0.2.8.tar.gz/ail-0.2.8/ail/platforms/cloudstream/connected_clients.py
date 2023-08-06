#-*- coding: utf-8 -*-
#
# Copyright © 2014 Jean des Morts <jean.des.morts@gmail.com>
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To Public License, Version 2,
# as published by Sam Hocevar. See the COPYING.WTFPL file for more details.

__author__ = 'jdmorts'

from ail import Profile
from ail.services.ssh import SSHService


class ConnectedClients(object):
    """
    """
    def __init__(self, output):
        try:
            self._clients = (output[0].split('s: ', 1)[1].replace(',', '').
                             split())

        except IndexError:
            self._clients = ()

    @property
    def clients(self):
        return self._clients


class SSHProfile(Profile):
    """
    """
    service = SSHService

    def __init__(self, cron_pid):
        self._cron_pid = cron_pid

    @property
    def _input(self):
        # Retrieve list of connected clients from streaming log
        return ("grep '({}) Connected clients:' tt_streaming.log | tail -n 1".
                format(self._cron_pid),)

    @staticmethod
    def _parse(output):
        return ConnectedClients(output)
