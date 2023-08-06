#-*- coding: utf-8 -*-
#
# Copyright © 2014 Jean des Morts <jean.des.morts@gmail.com>
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To Public License, Version 2,
# as published by Sam Hocevar. See the COPYING.WTFPL file for more details.

__author__ = 'jdmorts'

import logging

from ail import Profile
from ail.services.service import Service


logger = logging.getLogger(__name__)


class Result(object):
    """Parse and store service output in a useful format"""

    def __init__(self, output):
        self._result = {}

        try:
            for record in output:
                try:
                    pass

                except IndexError:
                    logger.warn('Unable to parse output {:s}'.format(record))

        except TypeError:
            raise TypeError('Unexpected output type {:s}'.format(type(output)))

    @property
    def result(self):
        return self._result


class ServiceProfile(Profile):
    """"""

    service = Service

    def __init__(self, some_arg):
        self._some_arg = some_arg

    @property
    def _input(self):
        return "Service input goes here " + self._some_arg,

    @staticmethod
    def _parse(output):
        return Result(output)
