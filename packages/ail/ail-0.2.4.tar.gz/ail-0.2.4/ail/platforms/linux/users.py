#-*- coding: utf-8 -*-
#
# Copyright © 2014 Jean des Morts <jean.des.morts@gmail.com>
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To Public License, Version 2,
# as published by Sam Hocevar. See the COPYING.WTFPL file for more details.

__author__ = 'jdmorts'

import logging
from datetime import datetime, timedelta

from ail import Profile
from ail.services.ssh import SSHService
from ail.util import make_to_xml, make_container

logger = logging.getLogger(__name__)

User = make_container('User', ('username', 'password', 'last_password_change'))


class Users(object):
    """Parse the Linux shadow file. The shadow struct contains the following:
    ::
     sp_namp - pointer to null-terminated user name
     sp_pwdp - pointer to null-terminated password
     sp_lstchg - days since Jan 1, 1970 password was last changed
     sp_min - days before which password may not be changed
     sp_max - days after which password must be changed
     sp_warn - days before password is to expire that user is warned of pending password expiration
     sp_inact - days after password expires that account is considered inactive and disabled
     sp_expire - days since Jan 1, 1970 when account will be disabled
     sp_flag - reserved for future use

    Example output:
    ::
     root:$1$b2111ecc$URgOh8cLs7JJWwsWbbLZz/:15126:0:::::
     bin:*:9797:0:::::
     daemon:*:9797:0:::::
     . . .
    """
    def __init__(self, output):
        self._users = {}
        self._to_xml = make_to_xml(())

        for record in (l.strip().split(':') for l in output):
            try:
                username = record[0]
                epoch = datetime(1970, 1, 1)
                last_change = (epoch.  # + timedelta(days=int(record[2]))).
                               isoformat())

                self._users[username] = User(*(record[:2] + [last_change]))

            except (IndexError, ValueError):
                # If not enough fields in record,
                logger.warn('Unable to parse user {:s}'.format(record))

    def __iter__(self):
        for user in self._users.itervalues():
            yield user

    def user(self, username):
        try:
            return self._users[username]

        except KeyError:
            # If no key exists for username,
            raise LookupError('Unknown username {:s}'.format(username))

        except TypeError:
            # If username is not hashable,
            raise TypeError('Invalid username type {:s}'.
                            format(type(username)))

    def to_xml(self, empty=False, indent=0):
        return self._to_xml(self, [u for u in self], indent=indent)


class SSHProfile(Profile):
    """
    """
    service = SSHService

    @property
    def _input(self):
        return "(sudo -n cat /etc/passwd || cat /etc/passwd) 2>/dev/null",

    @staticmethod
    def _parse(output):
        return Users(output)
