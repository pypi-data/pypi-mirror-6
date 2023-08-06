#-*- coding: utf-8 -*-
#
# Copyright © 2014 Jean des Morts <jean.des.morts@gmail.com>
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To Public License, Version 2,
# as published by Sam Hocevar. See the COPYING.WTFPL file for more details.

__author__ = 'jdmorts'

from ail import Service


class SNMPService(Service):
    """"""

    def __str__(self):
        return 'SnmpService(%s, %s)'.format(self._address, self._credential)

    def __init__(self, address, credential):
        super(SNMPService, self).__init__(address, credential)
