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

logger = logging.getLogger(__name__)

Login = make_container('Login', ('username', 'tty', 'timestamp', 'duration',
                                 'source'))


class Logins(object):
    """Parse output from the 'last' command, which parses /var/log/wtmp.

    The following example includes output from 'last -aFi', but '-F' isn't
    always available:
    ::
     -0600
     root   pts/2        Wed Feb 19 14:45:52 2014   still logged in       172.2.81.60
     root   pts/2        Wed Feb 19 14:45:51 2014 - 14:45:51  (00:00)     172.2.81.60
     . . .
     root   pts/1        Tue Feb 18 11:22:51 2014 - 13:40:11  (1+02:17)   172.2.81.60
     . . .
     wtmp begins Mon Feb 17 10:43:39 2014


    The next example, which uses the current commands from _input(), ist nicht
    so gut:
    ::
     -0600
     root   pts/3        Fri Feb 28 02:48   still logged in    172.2.81.60
     root   pts/3        Fri Feb 28 02:47 - 02:47  (00:00)     172.2.81.60
     root   pts/3        Fri Feb 28 02:47 - 02:47  (00:00)     172.2.81.60
     root   pts/3        Fri Feb 28 02:47 - 02:47  (00:00)     172.2.81.60
     root   pts/3        Fri Feb 28 02:47 - 02:47  (00:00)     172.2.81.60
     . . .
     wtmp begins Mon Feb 17 10:43:39 2014


    Without the '-F' switch, it becomes impossible to produce an accurate year.
    The best we can do is start with the current year and subtract from it every
    time we observe a date that appears to be later than the last one. Though
    wtmp's monotonicity allows us this much, it hardly constitutes good practice
    if the dates need to be accurate, which they do.
    """
    def __init__(self, output, last_only=False):
        self._logins = {}
        self._to_xml = make_to_xml(())

        try:
            tz = output.pop(0).strip()

        except IndexError:
            raise ValueError('Unable to initialize LastLogins object')

        # Start big, nasty kludge to deal with missing year in output
        last_date = datetime.now()
        year = last_date.year

        for line in output:
            try:
                # Parse output into sensible chunks
                username, tty, day_of_week, vestige = line.split(None, 3)
                # month, day, time, year, vestige = vestige.split(None, 4)
                month, day, time, vestige = vestige.split(None, 3)
                vestige, duration, source = vestige.rsplit(None, 2)

            except ValueError:
                logger.warn('Unable to parse last_login {:s}'.format(line))
                continue
            # Create datetime object from the local time
            date = datetime.strptime(' '.join((day_of_week, month, day,
                                               time, str(year))),
                                     "%a %b %d %H:%M %Y")
            # If time appears to reverse, decrement the year by one
            if date > last_date:
                year -= 1
                date.replace(year=year)
            # Set last_date to this one and convert to UTC in ISO 8601 format
            last_date = date
            utc = adjust_time(date, tz)
            timestamp = utc.replace(tzinfo=pytz.UTC).isoformat()

            if duration == 'in':
                duration = 'still logged in'
            else:
                duration = duration.strip('()')
                # Detect days in duration output
                if '+' in duration:
                    days, hm = duration.split('+', 1)
                else:
                    days, hm = 0, duration
                # Calculate months, years from days for ISO 8601 format
                hours, minutes = hm.split(':', 1)
                months, days = divmod(int(days), 30)
                years, months = divmod(months, 12)
                duration = 'P{}Y{}M{}DT{}H{}M00S'.format(str(years).zfill(4),
                                                         str(months).zfill(2),
                                                         str(days).zfill(2),
                                                         hours.zfill(2),
                                                         minutes.zfill(2))
            # If last_only==True, capture only the first (most recent) login
            if last_only is True and username in self._logins:
                continue
            # Create a new Login object
            login = Login(username, tty, timestamp, duration, source)
            # Store the login in our internal dict
            try:
                self._logins[username].append(login)

            except KeyError:
                self._logins[username] = [login]

    def __iter__(self):
        for logins in [self._logins[u] for u in sorted(self._logins.keys())]:
            for login in logins:
                yield login

    def logins(self, username):
        try:
            return self._logins[username]

        except KeyError:
            raise LookupError('Unknown username {:s}'.format(username))

        except TypeError:
            raise TypeError('Invalid username type {:s}'.
                            format(type(username)))

    def to_xml(self, empty=False, indent=0, tag='logins'):
        return self._to_xml(self, [u for u in self], indent=indent, tag=tag)


class SSHProfile(Profile):
    """
    """
    service = SSHService

    @property
    def _input(self):
        # TODO: Replace 'last' command with raw wtmp access. And hate.
        return ("date '+%:::z'",
                "last -ai 2>/dev/null | head -n -2 | egrep -v '^reboot'")

    @staticmethod
    def _parse(output):
        return Logins(output)
