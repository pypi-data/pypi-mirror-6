#-*- coding: utf-8 -*-
#
# Copyright © 2014 Jean des Morts <jean.des.morts@gmail.com>
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To Public License, Version 2,
# as published by Sam Hocevar. See the COPYING.WTFPL file for more details.

__author__ = 'jdmorts'

import logging

from .logins import SSHProfile as LoginsSSHProfile
from .logins import Logins

logger = logging.getLogger(__name__)


class LastLogins(object):
    """Delegates to Logins to return only the most recent logins.
    """
    def __init__(self, output, last_only=True):
        self._logins = Logins(output, last_only=last_only)

    def __iter__(self):
        for login in self._logins:
            yield login

    def last_login(self, username):
        return self._logins.logins(username)

    def to_xml(self, empty=False, indent=0, tag='last_logins'):
        return self._logins.to_xml(empty=empty, indent=indent, tag=tag)


class SSHProfile(LoginsSSHProfile):
    """
    """
    @staticmethod
    def _parse(output):
        return LastLogins(output)
