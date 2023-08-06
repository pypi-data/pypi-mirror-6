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
from ail.util import make_to_xml, make_container, adjust_time


logger = logging.getLogger()

LastLogin = make_container('LastLogin', ('username', 'tty', 'timestamp',
                                         'duration', 'source'))


class LastLogins(object):
    """Parse output from the 'last' command, which parses /var/log/wtmp

    Example output:

    -0600
    root   pts/2        Wed Feb 19 14:45:52 2014   still logged in                       172.2.81.60
    root   pts/2        Wed Feb 19 14:45:51 2014 - Wed Feb 19 14:45:51 2014  (00:00)     172.2.81.60
    . . .
    root   pts/1        Tue Feb 18 11:22:51 2014 - Wed Feb 19 13:40:11 2014  (1+02:17)   172.2.81.60
    . . ."""

    def __init__(self, output):
        self._last_logins = {}
        self._to_xml = make_to_xml(())

        try:
            tz = output.pop(0).strip()

        except IndexError:
            raise ValueError('Unable to initialize LastLogins object')

        except TypeError:
            raise TypeError('Unexpected output type {:s}'.format(type(output)))

        for line in (l.strip() for l in output):
            try:
                username, tty, day_of_week, vestige = line.split(None, 3)
                month, day, time, year, vestige = vestige.split(None, 4)
                vestige, duration, source = line.rsplit(None, 2)
                local = datetime.strptime(' '.join((day_of_week, month, day,
                                                    time, year)),
                                          "%a %b %d %H:%M:%S %Y")

                utc = adjust_time(local, tz)
                # Make datetime object timezone-aware
                timestamp = utc.replace(tzinfo=pytz.UTC).isoformat()

            except IndexError:
                logger.warn('Unable to parse last_login {:s}'.format(line))
                continue

            if duration == 'in':
                duration = 'still logged in'

            else:
                duration = duration.strip('()')

                if '+' in duration:
                    days, hm = duration.split('+', 1)
                else:
                    days, hm = 0, duration

                hours, minutes = hm.split(':', 1)
                months, days = divmod(int(days), 30)
                years, months = divmod(months, 12)
                duration = 'P{}Y{}M{}DT{}H{}M00S'.format(str(years).zfill(4),
                                                         str(months).zfill(2),
                                                         str(days).zfill(2),
                                                         hours.zfill(2),
                                                         minutes.zfill(2))

            if username not in self._last_logins:
                login = LastLogin(username, tty, timestamp, duration, source)
                self._last_logins[username] = login

    def __iter__(self):
        for login in [self._last_logins[u] for u in sorted(self._last_logins.keys())]:
            yield login

    def last_login(self, username):
        try:
            return self._last_logins[username]

        except KeyError:
            raise LookupError('Unknown username {:s}'.format(username))

        except TypeError:
            raise TypeError('Invalid username type {:s}'.
                            format(type(username)))

    def to_xml(self, empty=False, indent=0):
        return self._to_xml(self, [u for u in self], indent=indent,
                            tag='last_logins')


class SSHProfile(Profile):
    """"""

    service = SSHService

    @property
    def _input(self):
        return ("date '+%:::z'",
                "last -awFi 2>/dev/null | head -n -2")

    @staticmethod
    def _parse(output):
        return LastLogins(output)
