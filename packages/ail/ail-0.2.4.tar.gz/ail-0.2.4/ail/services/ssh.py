#-*- coding: utf-8 -*-
#
# Copyright © 2014 Jean des Morts <jean.des.morts@gmail.com>
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To Public License, Version 2,
# as published by Sam Hocevar. See the COPYING.WTFPL file for more details.

__author__ = 'jdmorts'

import logging
import socket
import paramiko
from ail import Service
from ail.util import AuthenticationError

logger = logging.getLogger(__name__)


class SSHService(Service):
    """
    """
    def __init__(self, credential, address, port=22):
        """Create new SSHService object.

        :param credential: an instance of the :class:`Credential` class
        :type credential: instance of :class:`Credential`
        :param address: platform location
        :type address: str
        :param port: port on which SSH service resides
        :type port: int
        """
        super(SSHService, self).__init__(credential, address)
        self._port = port
        # Scrub, organize credentials
        try:
            username = self._credential.usernames[0]

        except IndexError:
            username = None

        try:
            password = self._credential.passwords[0]

        except IndexError:
            password = None

        try:
            keystr = self._credential.keys[0]
            pkey = paramiko.RSAKey.from_private_key(keystr)

        except (IndexError, IOError, paramiko.SSHException,
                paramiko.PasswordRequiredException):
            # If no key was given, or the key was unable to be read,
            # or what we read was invalid, or if the key requires a password,
            pkey = None

        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # Connect
        try:
            client.connect(self._address, port=self._port, username=username,
                           password=password, pkey=pkey, timeout=10)

        except paramiko.AuthenticationException as e:
            # If unable to authenticate,
            raise AuthenticationError(('Unable to authenticate to address ' +
                                       '{} using credential ' +
                                       '({:s}, {:s}, {:s})').
                                      format(address, port,
                                             username, password, pkey))

        except (paramiko.SSHException, socket.error) as e:
            # If unable to connect,
            raise IOError('Unable to connect to address {:s}:{:s}: {:s}'.
                          format(self._address, self._port, e))

        self._client = client

    def __repr__(self):
        return 'SSHService({:s}:{:s}, {:s})'.format(self._address, self._port,
                                                    self._credential)

    def send(self, input, timeout=10):
        self._output = []
        self._errout = []
        # Test input for type consistency
        try:
            len(input)

        except TypeError:
            raise TypeError('Invalid input type {:s}'.format(type(input)))
        # Send and receive
        for command in input:
            try:
                __, stdout, stderr = (self._client.exec_command(command,
                                                                get_pty=True,
                                                                timeout=timeout))

            except (paramiko.SSHException, socket.timeout) as e:
                # If sending the command fails,
                raise IOError('Unable to send command {:s} to address {:s}'.
                              format(command, self._address))

            try:
                self._output += [l.rstrip('\n\r')
                                 for l in stdout.readlines()]

                self._errout += [l.rstrip('\n\r')
                                 for l in stderr.readlines()]

            except (AttributeError, TypeError) as e:
                # If we receive unexpected output,
                raise IOError(('Unable to retrieve output for command {} ' +
                              'from address {:s}').
                              format(command, self._address))
