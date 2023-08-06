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

Netstat = make_container('Netstat', ('proto', 'local_address', 'local_port',
                                     'foreign_address', 'foreign_port',
                                     'state', 'program'))


class Netstats(object):
    """Expected output:
    ::
     Active Internet connections (servers and established)
     Proto Recv-Q Send-Q Local Address           Foreign Address         State       PID/Program name
     tcp        0      0 0.0.0.0:21              0.0.0.0:*               LISTEN      1606/inetd
     tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN      7611/sshd
     . . .
     udp6       0      0 :::123                  :::*                                8348/ntpd
     udp6       0      0 ::1:45788               ::1:45788               ESTABLISHED 1738/postgres
    """
    def __init__(self, output):
        self._netstats = {}
        self._local_ports = ()
        self._to_xml = make_to_xml(())

        try:
            del output[:2]

        except ValueError:
            raise ValueError("Unexpected output value")

        for record in (l.strip().split() for l in output):
            try:
                proto = record[0]
                program = record[-1]
                state = ''
                laddr, lport = record[3].rsplit(':', 1)
                faddr, fport = record[4].rsplit(':', 1)
                # udp/udp6 may have state 'ESTABLISHED'. If so, store it
                if len(record) == 7:
                    state = record[5]

            except (IndexError, ValueError):
                logger.warn('Unable to parse netstat {:s}'.format(record))
                continue

            netstat = Netstat(proto, laddr, lport, faddr, fport, state,
                              program)

            if netstat.local_port not in self._netstats:
                self._netstats[netstat.local_port] = []

            self._netstats[netstat.local_port].append(netstat)

        self._sorted_ports = tuple(sorted(self._netstats.keys(), key=int))

    def __iter__(self):
        for netstats in (self._netstats[p] for p in self._sorted_ports):
            for netstat in netstats:
                yield netstat

    def netstat(self, local_port):
        try:
            return tuple(self._netstats[local_port])

        except KeyError:
            raise LookupError("Unknown local_port {:s}".format(local_port))

        except TypeError:
            raise TypeError("Invalid local_port type {:s}".
                            format(type(local_port)))

    def to_xml(self, empty=False, indent=0):
        return self._to_xml(self, [u for u in self], indent=indent)


class SSHProfile(Profile):
    """
    """
    service = SSHService

    @property
    def _input(self):
        # On some systems, -W prevents address truncation. On others, -T does.
        return ("output=$((sudo -n netstat -anpWtu" +
                "    || sudo -n netstat -anpTtu) 2>/dev/null" +
                "    | egrep -v '^$'); " +
                "if [ -z \"$output\" ]; then " +
                "    (netstat -anpWtu || netstat -anpTtu) 2>/dev/null" +
                "        | egrep -v '^$'; " +
                "else echo \"$output\"; fi",)

    @staticmethod
    def _parse(output):
        return Netstats(output)
