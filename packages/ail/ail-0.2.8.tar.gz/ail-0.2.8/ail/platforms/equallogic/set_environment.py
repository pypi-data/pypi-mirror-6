#-*- coding: utf-8 -*-
#
# Copyright © 2014 Jean des Morts <jean.des.morts@gmail.com>
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To Public License, Version 2,
# as published by Sam Hocevar. See the COPYING.WTFPL file for more details.

__author__ = 'jdmorts'

from ail import Profile
from ail.services.telnet import EqualLogicCLIService


class TelnetProfile(Profile):
    """Set sane EqualLogic CLI environment settings.
    """
    service = EqualLogicCLIService

    @property
    def _input(self):
        return (("", "cli-settings events off"),
                ("", "stty columns 255"),
                ("", "stty hardwrap off"),
                ("", "cli-settings formatoutput off"),
                ("", "cli-settings paging off"),
                ("", "cli-settings confirmation off"))

    @staticmethod
    def _parse(output):
        return None
