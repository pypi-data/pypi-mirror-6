#-*- coding: utf-8 -*-
#
# Copyright © 2014 Jean des Morts <jean.des.morts@gmail.com>
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To Public License, Version 2,
# as published by Sam Hocevar. See the COPYING.WTFPL file for more details.

__author__ = 'jdmorts'

from ail import Profile
from ail.services.ssh import SSHService


class CronLog(object):
    """
    """
    def __init__(self, output):
        try:
            self._command = (output[0].rstrip().split('CMD (', 1)[1].lstrip().
                             rstrip(')'))

        except IndexError:
            self._command = ''

    @property
    def command(self):
        return self._command


class SSHProfile(Profile):
    """
    """
    service = SSHService

    def __init__(self, cron_pid):
        self._cron_pid = cron_pid

    @property
    def _input(self):
        # Retrieve the last run cron job for user 'jesolutions'
        return ("sudo -n grep 'CRON\[{}\]' /var/log/syslog | grep '({})' " +
                "| tail -n 1").format(self._cron_pid, 'jesolutions'),

    @staticmethod
    def _parse(output):
        return CronLog(output)
