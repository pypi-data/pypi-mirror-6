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

from ail import Profile
from ail.services.ssh import SSHService
from ail.util import adjust_time, make_container, make_to_xml

logger = logging.getLogger(__name__)

Login = make_container('Login', ('source', 'source_port', 'user', 'timestamp',
                                 'process', 'reason'))


class FailedLogins(object):
    """Expected output:
    ::
     -0600
     Mar  2 06:17:33 anbox sshd[5379]: Failed password for invalid user 0 from 74.63.242.122 port 47742 ssh2
     Mar  2 06:04:23 anbox sshd[4764]: Failed password for invalid user music from 37.187.57.167 port 51552 ssh2
     Mar  2 05:47:56 anbox sshd[3986]: Failed password for invalid user music from 37.187.57.167 port 37677 ssh2
     Mar  2 04:58:32 anbox sshd[1594]: Failed password for invalid user music from 37.187.57.167 port 52513 ssh2
     Mar  2 04:42:03 anbox sshd[801]: Failed password for invalid user music from 37.187.57.167 port 38633 ssh2
    """
    def __init__(self, output):
        self._logins = {}
        self._to_xml = make_to_xml(())

        try:
            tz = output.pop(0).strip()

        except IndexError:
            raise ValueError('Unable to initialize FailedLogins object: ' +
                             'no output received')

        if not output:
            raise ValueError('Unable to initialize FailedLogins object: ' +
                             'got timezone but no further output')

        # Start big, nasty kludge to deal with missing year in output
        last_date = datetime.now()
        year = last_date.year

        for line in output:
            try:
                # Parse output into sensible chunks
                month, day, time, __, process, vestige = line.split(None, 5)
                vestige, source, __, port, __ = vestige.rsplit(None, 4)
                vestige, reason, user, __ = vestige.rsplit(None, 3)

            except ValueError:
                logger.warn('Unable to parse failed login {:s}'.format(line))
                continue

            # Create datetime object from the local time
            date = datetime.strptime(' '.join((month, day, time, str(year))),
                                     "%b %d %H:%M:%S %Y")
            # If time appears to reverse, decrement the year by one
            if date > last_date:
                year -= 1
                date.replace(year=year)
            # Set last_date to this one and convert to UTC in ISO 8601 format
            last_date = date
            utc = adjust_time(date, tz)
            timestamp = utc.replace(tzinfo=pytz.UTC).isoformat()
            # Remove colon from end of process
            process = process.rstrip(':')
            # Interpret reason for failure
            reason = 'username' if reason == 'user' else 'password'
            # Create a new Login object
            login = Login(source, port, user, timestamp, process, reason)
            # Store the login in our internal dict
            try:
                self._logins[source].append(login)

            except KeyError:
                self._logins[source] = [login]

    def __iter__(self):
        for source_logins in self._logins.itervalues():
            for login in source_logins:
                yield login

    def failed_logins(self, source_ip):
        try:
            return self._logins[source_ip]

        except KeyError:
            # If no key exists for username,
            raise LookupError('Unknown source {:s}'.format(source_ip))

        except TypeError:
            # If username is not hashable,
            raise TypeError('Invalid source type {:s}'.
                            format(type(source_ip)))

    def to_xml(self, empty=False, indent=0, tag='failed_logins'):
        return self._to_xml(self, [l for l in self], indent=indent, tag=tag)


class SSHProfile(Profile):
    """
    """
    service = SSHService

    @property
    def _input(self):
        return ("date '+%:::z'",
                "((cat /var/log/messages" +
                "  || sudo -n cat /var/log/messages)" +
                " 2>/dev/null; "
                " (zcat /var/log/messages*.gz" +
                "  || sudo -n zcat /var/log/messages*.gz)" +
                " 2>/dev/null; "
                " (cat /var/log/secure*" +
                "  || sudo -n cat /var/log/secure*)" +
                " 2>/dev/null) " +
                "| grep -i 'failed password' | sort -r")

    @staticmethod
    def _parse(output):
        return FailedLogins(output)
