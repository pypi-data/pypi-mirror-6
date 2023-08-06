#-*- coding: utf-8 -*-
#
# Copyright © 2014 Jean des Morts <jean.des.morts@gmail.com>
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To Public License, Version 2,
# as published by Sam Hocevar. See the COPYING.WTFPL file for more details.

__author__ = 'jdmorts'

import logging
import pexpect
from ail import Service
from ail.util import AuthenticationError

logger = logging.getLogger(__name__)


class TelnetService(Service):
    """
    """
    def __init__(self, credential, address, port=23):
        """Create new TelnetService object.

        :param credential: an instance of the :class:`Credential` class
        :type credential: instance of :class:`Credential`
        :param address: platform location
        :type address: str
        :param port: port on which Telnet service resides
        :type port: int
        """
        super(TelnetService, self).__init__(credential, address)
        self._port = port
        # Scrub, organize credentials
        try:
            self._username = self._credential.usernames[0]

        except IndexError:
            self._username = ''

        try:
            self._password = self._credential.passwords[0]

        except IndexError:
            self._password = ''

        try:
            self._child = pexpect.spawn('telnet', ['-N', self._address,
                                                   str(port)])

        except pexpect.ExceptionPexpect as e:
            raise IOError('Unable to spawn telnet: {:s}'.format(e))

    def __repr__(self):
        return 'TelnetService({}, {:s})'.format(self._address, self._credential)


class EqualLogicCLIService(TelnetService):
    """
    """
    def __init__(self, credential, address, port=23):
        """Create new EqualLogicCLIService object.

        :param credential: an instance of the :class:`Credential` class
        :type credential: instance of :class:`Credential`
        :param address: platform location
        :type address: str
        :param port: port on which Telnet service resides
        :type port: int
        """
        super(EqualLogicCLIService, self).__init__(credential, address, port)
        self._prompt = '>'
        max_retries = 3
        # Authenticate
        for retry in range(1, max_retries):
            try:
                self._child.expect_exact('login:')
                self._child.sendline(self._username)
                self._child.expect_exact('Password:')
                self._child.sendline(self._password)
                self._child.expect_exact(self._prompt)
                break

            except pexpect.ExceptionPexpect:
                # When login fails, if we've reached max_retries,
                if retry == max_retries:
                    raise AuthenticationError(('Unable to connect to address ' +
                                               '{:s}').format(address))

        try:
            # Retrieve the complete prompt and use it for future expects
            self._prompt = ''.join((self._child.before.rsplit('\r\n', 2)[-1],
                                    self._prompt))

        except pexpect.ExceptionPexpect:
            # If we're unable to retrieve output,
            raise IOError('Unable to retrieve prompt for address {:s}'.
                          format(address))

        self._child.setecho(False)

    def send(self, input):
        self._output = []
        # Test input for type consistency
        try:
            len(input[0])

        except (IndexError, TypeError):
            raise TypeError('Invalid input type {:s}'.format(type(input)))
        # Send and receive
        for pattern, command in (t for t in input):
            try:
                # If no pattern is given, default to expect prompt
                if not pattern:
                    pattern = self._prompt

                self._child.send(command + '\r')
                self._child.expect(pattern)
                self._output += self._child.before.split('\r\n')

            except pexpect.TIMEOUT:
                # If our expect times out,
                raise IOError('Pexpect timeout on command {:s}'.
                              format(command))

            except (AttributeError, pexpect.ExceptionPexpect) as e:
                # If unable to split output, or some other failure,
                raise IOError('Unable to retrieve output from address {}'.
                              format(self._address))
