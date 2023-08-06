#-*- coding: utf-8 -*-
#
# Copyright © 2014 Jean des Morts <jean.des.morts@gmail.com>
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To Public License, Version 2,
# as published by Sam Hocevar. See the COPYING.WTFPL file for more details.

__author__ = 'jdmorts'

import logging

from ail import Platform, CachedOperation
from . import (connected_clients, cron_log, server_status)

logger = logging.getLogger()


class CloudStreamEdgePlatform(Platform):
    """Interface to the CloudStream Edge Server. All operations are achieved using
    the SSH service module."""

    def __init__(self, address):
        super(CloudStreamEdgePlatform, self).__init__('CloudStreamEdge', address)

    @CachedOperation
    @property
    def connected_clients(self):
        """"""

        status = self.server_status()
        return self._execute_profiles(connected_clients.SSHProfile(status.pid))

    @CachedOperation
    @property
    def cron_log(self):
        """"""

        status = self.server_status()
        return self._execute_profiles(cron_log.SSHProfile(status.pid))

    @CachedOperation
    @property
    def server_status(self):
        """"""

        return self._execute_profiles(server_status.SSHProfile())
