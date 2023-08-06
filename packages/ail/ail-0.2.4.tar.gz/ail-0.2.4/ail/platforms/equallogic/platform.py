#-*- coding: utf-8 -*-
#
# Copyright © 2014 Jean des Morts <jean.des.morts@gmail.com>
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To Public License, Version 2,
# as published by Sam Hocevar. See the COPYING.WTFPL file for more details.

__author__ = 'jdmorts'

import logging

from ail import Platform, CachedOperation
from . import (add_volume_ace, set_environment, volume_acl, volumes)

logger = logging.getLogger(__name__)


class EqualLogic(Platform):
    """Interface to the Dell EqualLogic CLI.

    All operations are achieved using the EqualLogicCLIService module.
    """
    def __init__(self, address):
        super(EqualLogic, self).__init__('EqualLogic', address)

    def add_volume_ace(self, volume_name, ace):
        """Add a new ACE to an existing volume ACL.

        :return: True if successful, False otherwise
        :rtype: bool
        """
        return self._execute_profiles(add_volume_ace.TelnetProfile(volume_name,
                                                                   ace))

    def set_environment(self):
        """Set sane EqualLogic CLI environment settings.

        :return: None
        :rtype: None
        """
        return self._execute_profiles(set_environment.TelnetProfile())

    def volume_acl(self, volume_name):
        """Retrieve a volume's access-list by volume name.

        Uses the 'volume select ... access show' command.

        :param volume_name: name as it appears in 'volume show' output
        :type volume_name: str
        :return: Iterable object containing ACE's
        :rtype: VolumeACL()
        """
        return self._execute_profiles(volume_acl.TelnetProfile(volume_name))

    @CachedOperation
    @property
    def volumes(self):
        """Retrieve volume information using the 'volume show' command.

        :return: Iterable object containing volume information
        :rtype: Volumes()
        """
        return self._execute_profiles(volumes.TelnetProfile())
