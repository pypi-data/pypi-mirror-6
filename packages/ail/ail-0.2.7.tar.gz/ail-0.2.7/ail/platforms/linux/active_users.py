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

User = make_container('User', ('username',))


class ActiveUsers(object):
    """
    """
    def __init__(self, output):
        self._active_users = {}
        self._to_xml = make_to_xml(())

        try:
            for user in (User(u) for u in output[0].strip().split(' ') if u):
                self._active_users[user.username] = user

        except IndexError:
            raise ValueError('Unable to initialize ActiveUsers object')

    def __iter__(self):
        for username in self._active_users.keys():
            yield self._active_users[username]

    def active_user(self, username):
        try:
            if username in self._active_users:
                return True
            else:
                return False

        except TypeError:
            raise TypeError('Invalid username type {:s}'.
                            format(type(username)))

    def to_xml(self, empty=False, indent=0):
        return self._to_xml(self, [u for u in self], indent=indent,
                            tag='active_users')


class SSHProfile(Profile):
    """
    """
    service = SSHService

    @property
    def _input(self):
        return "users 2>/dev/null",

    @staticmethod
    def _parse(output):
        return ActiveUsers(output)
