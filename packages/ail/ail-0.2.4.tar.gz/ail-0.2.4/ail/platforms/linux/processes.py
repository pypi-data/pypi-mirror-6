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

Process = make_container('Process', ('pid', 'ppid', 'cpu', 'mem', 'stat',
                                     'started', 'time', 'user', 'command'))


class Processes(object):
    """Expected output:
    ::

     -0600
       PID  PPID %CPU %MEM STAT                  STARTED       TIME USER                      COMMAND
         1     0  0.0  0.0 Ss   Wed Nov 20 20:57:35 2013   00:01:52 root                      init [3]
         2     0  0.0  0.0 S    Wed Nov 20 20:57:35 2013   00:00:00 root                      [kthreadd]
         3     2  0.0  0.0 S    Wed Nov 20 20:57:35 2013   00:00:04 root                      [ksoftirqd/0]
         4     2  0.0  0.0 S    Wed Nov 20 20:57:35 2013   00:01:29 root                      [kworker/0:0]
     . . .
      1970     1  1.4  5.7 Sl   Tue Nov 26 22:12:17 2013 1-05:02:42 rabbitmq                  /usr/...
     . . .
    """
    def __init__(self, output):
        self._processes = {}
        self._sorted_pids = []
        self._to_xml = make_to_xml(())

        try:
            tz = output.pop(0).strip()  # Capture UTC offset
            del output[0]  # Remove column headers

        except IndexError:
            raise ValueError("Unable to initialize Processes object")

        for record in (l.strip().split() for l in output):
            try:
                local = datetime.strptime(' '.join(record[5:10]),
                                          "%a %b %d %H:%M:%S %Y")

                utc = adjust_time(local, tz)
                # Make datetime object timezone-aware
                started = utc.replace(tzinfo=pytz.UTC).isoformat()
                if '-' in record[10]:
                    days, hms = record[10].split('-')
                else:
                    days, hms = 0, record[10]

                hours, minutes, seconds = hms.split(':', 2)
                months, days = divmod(int(days), 30)
                years, months = divmod(months, 12)
                cpu_time = 'P{}Y{}M{}DT{}H{}M{}S'.format(str(years).zfill(4),
                                                         str(months).zfill(2),
                                                         str(days).zfill(2),
                                                         hours.zfill(2),
                                                         minutes.zfill(2),
                                                         seconds.zfill(2))

                process = Process(*(record[0:5] +
                                    [started, cpu_time, record[11]] +
                                    [' '.join(record[12:])]))

                self._processes[process.pid] = process

            except (IndexError, ValueError):
                # If not enough fields in record,
                logger.warn('Unable to parse process {:s}'.format(record))

        self._sorted_pids = sorted(self._processes.keys(), key=int)

    def __iter__(self):
        for pid in self._sorted_pids:
            yield self._processes[pid]

    def process(self, pid):
        try:
            return self._processes[pid]

        except KeyError:
            raise LookupError('Unknown pid {:s}'.format(pid))

        except TypeError:
            raise TypeError('Invalid pid type {:s}'.format(type(pid)))

    def to_xml(self, empty=False, indent=0):
        return self._to_xml(self, [p for p in self], indent=indent)


class SSHProfile(Profile):
    """"""

    service = SSHService

    @property
    def _input(self):
        """Get the UTC offset and running processes. 'user:25' prevents usernames
        being replaced with UID's when exceeding the default column width."""

        return ("date '+%:::z'",
                "ps axwo pid,ppid,pcpu,pmem,stat,lstart,time,user:25,args")

    @staticmethod
    def _parse(output):
        return Processes(output)
