#-*- coding: utf-8 -*-
#
# Copyright © 2014 Jean des Morts <jean.des.morts@gmail.com>
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To Public License, Version 2,
# as published by Sam Hocevar. See the COPYING.WTFPL file for more details.

__author__ = 'jdmorts'

import logging
from datetime import datetime

import pytz

from ail import IterablePlatform, CachedOperation
from . import (active_users, distribution, failed_logins, groups, hostname,
               kernel, last_logins, logins, mounts, netstats, packages,
               processes, sshd_permit_root, sudo_logs, users)

from ail.util import make_to_xml

logger = logging.getLogger(__name__)


class Linux(IterablePlatform):
    """
    """
    def __init__(self, address):
        super(Linux, self).__init__('Linux', address)
        self._to_xml = make_to_xml(('type', 'address', 'scan_time'))

    @CachedOperation
    @property
    def active_users(self):
        """
        """
        return self._execute_profiles(active_users.SSHProfile())

    @CachedOperation
    @property
    def distribution(self):
        """
        """
        return self._execute_profiles(distribution.SSHProfile())

    @CachedOperation
    @property
    def failed_logins(self):
        """
        """
        return self._execute_profiles(failed_logins.SSHProfile())

    @CachedOperation
    @property
    def groups(self):
        """
        """
        return self._execute_profiles(groups.SSHProfile())

    @CachedOperation
    @property
    def hostname(self):
        """
        """
        return self._execute_profiles(hostname.SSHProfile())

    @CachedOperation
    @property
    def kernel(self):
        """
        """
        return self._execute_profiles(kernel.SSHProfile())

    @CachedOperation
    @property
    def last_logins(self):
        """
        """
        return self._execute_profiles(last_logins.SSHProfile())

    @CachedOperation
    @property
    def logins(self):
        """
        """
        return self._execute_profiles(logins.SSHProfile())

    @CachedOperation
    @property
    def mounts(self):
        """
        """
        return self._execute_profiles(mounts.SSHProfile())

    @CachedOperation
    @property
    def netstats(self):
        """
        """
        return self._execute_profiles(netstats.SSHProfile())

    @CachedOperation
    @property
    def packages(self):
        """
        """
        return self._execute_profiles(packages.SSHProfile())

    @CachedOperation
    @property
    def processes(self):
        """
        """
        return self._execute_profiles(processes.SSHProfile())

    @CachedOperation
    @property
    def scan_time(self):
        """
        """
        return datetime.now(pytz.UTC).isoformat()

    @CachedOperation
    @property
    def sshd_permit_root(self):
        """
        """
        return self._execute_profiles(sshd_permit_root.SSHProfile())

    @CachedOperation
    @property
    def sudo_logs(self):
        """
        """
        return self._execute_profiles(sudo_logs.SSHProfile())

    @CachedOperation
    @property
    def users(self):
        """
        """
        return self._execute_profiles(users.SSHProfile())
