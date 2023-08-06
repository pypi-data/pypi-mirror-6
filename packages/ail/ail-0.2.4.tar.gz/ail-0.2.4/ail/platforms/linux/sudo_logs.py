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

Log = make_container('Log', ('user', 'timestamp', 'tty', 'pwd', 'pseudo',
                             'command'))


class SudoLogs(object):
    """Expected output:
    ::
     -0600
     Feb 10 13:46:49 anbox sudo: anuser : TTY=pts/0 ; PWD=/home/anuser/dev/working ; USER=root ; COMMAND=/usr/bin/tail -f /var/log/cron
     Feb 10 18:12:11 anbox sudo: anuser : TTY=pts/0 ; PWD=/home/anuser/dev/working ; USER=root ; COMMAND=/etc/rc.d/rc.ntpd status
     Feb 10 19:48:16 anbox sudo: anuser : TTY=pts/0 ; PWD=/home/anuser/dev/working ; USER=root ; COMMAND=/usr/bin/grep 24709 /var/log/cron
     Feb 10 19:48:23 anbox sudo: anuser : TTY=pts/0 ; PWD=/home/anuser/dev/working ; USER=root ; COMMAND=/usr/bin/tail /var/log/cron
     Mar 10 19:58:02 anbox sudo: anuser : a password is required ; TTY=pts/2 ; PWD=/home/anuser ; USER=root ; COMMAND=/usr/bin/cat /var/log/secure /var/log/secure.1 /var/log/secure.2 /var/log/secure.3 /var/log/secure.4
    """
    def __init__(self, output):
        self._sudologs = {}
        self._to_xml = make_to_xml(())

        try:
            tz = output.pop(0).strip()

        except IndexError:
            raise ValueError('Unable to initialize SudoLogs object: ' +
                             'no output received')

        if not output:
            raise ValueError('Unable to initialize SudoLogs object: ' +
                             'got timezone but no further output')

        # Start big, nasty kludge to deal with missing year in output
        last_date = datetime.now()
        year = last_date.year

        for line in output:
            try:
                # Parse output into sensible chunks
                month, day, time, __, __, user, vestige = line.split(None, 6)
                __, vestige = vestige.split('=', 1)
                tty, __, pwd, __, pseudo, vestige = vestige.split(None, 5)
                __, command = vestige.split(None, 1)

            except ValueError:
                logger.warn('Unable to parse sudo log {:s}'.format(line))
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
            # Remove "XXXX=" from log elements
            args = [i.split('=', 1)[1] for i in (pwd, pseudo, command)]
            # Create a new Log object
            sudolog = Log(user, timestamp, tty, *args)
            # Store the log in our internal dict
            try:
                self._sudologs[user].append(sudolog)

            except KeyError:
                self._sudologs[user] = [sudolog]

    def __iter__(self):
        for user_logs in self._sudologs.itervalues():
            for log in user_logs:
                yield log

    def sudo_logs(self, username):
        try:
            return self._sudologs[username]

        except KeyError:
            # If no key exists for username,
            raise LookupError('Unknown username {:s}'.format(username))

        except TypeError:
            # If username is not hashable,
            raise TypeError('Invalid username type {:s}'.
                            format(type(username)))

    def to_xml(self, empty=False, indent=0, tag='sudo_logs'):
        return self._to_xml(self, [c for c in self], indent=indent, tag=tag)


class SSHProfile(Profile):
    """
    """
    service = SSHService

    @property
    def _input(self):
        return ("date '+%:::z'",
                "(cat /var/log/secure* || sudo -n cat /var/log/secure*) " +
                "2>/dev/null | grep -i ' sudo:' | sort -r")

    @staticmethod
    def _parse(output):
        return SudoLogs(output)
