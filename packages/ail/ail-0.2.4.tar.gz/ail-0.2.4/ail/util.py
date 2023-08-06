#-*- coding: utf-8 -*-
#
# Copyright © 2014 Jean des Morts <jean.des.morts@gmail.com>
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To Public License, Version 2,
# as published by Sam Hocevar. See the COPYING.WTFPL file for more details.

__author__ = 'jdmorts'

from collections import namedtuple
from datetime import timedelta
from xml.sax.saxutils import quoteattr


class AuthenticationError(Exception):
    pass


def adjust_time(dt_object, string):
    if string.startswith('-'):
        string = string[1:]
        return dt_object - timedelta(hours=int(string))

    elif string.startswith('+'):
        string = string[1:]
        return dt_object + timedelta(hours=int(string))

    else:
        return dt_object + timedelta(hours=int(string))


def make_container(obj_type, obj_attrs):
    klass = namedtuple(obj_type, obj_attrs)
    klass.to_xml = make_to_xml(obj_attrs)

    return klass


def make_to_xml(obj_attrs):
    """Attach a to_xml() method to the provided class. Provided attributes make
    up the XML element attributes.

    :param obj_attrs: attributes of the target object
    :type obj_attrs: seq
    :return: function suitable for use as a class method
    :rtype: function reference
    """
    def to_xml(self, c_objects=tuple(), empty=False, indent=0, tag=''):
        """Return XML representation of 'self' as single element with attributes.
        Optionally, additional objects may provide this element's content.

        :param c_objects: objects from which to obtain our element's content
        :type c_objects: list of objects with our .to_xml() method
        :param empty: when true, try to make empty element ('/>')
        :type empty: bool
        :param indent: indents the resulting output by 'indent' spaces
        :type indent: int
        :param tag: overrides the default tag of self.__class__.__name__
        :type tag: str
        :return: resulting XML
        :rtype: str
        """
        if not tag:
            tag = self.__class__.__name__

        tag = tag.lower()
        xml = '<{}'.format(tag)

        for attr in obj_attrs:
            value = quoteattr(str(getattr(self, attr)))
            xml = ''.join((xml, ' {}={}'.format(attr, value)))

        content = ''

        for c_object in c_objects:
            try:
                content = ''.join((content,
                                   c_object.to_xml(empty=True, indent=2)))

                empty = False

            except AttributeError:
                # Protect ourselves from objects lacking a to_xml() method
                pass

        if empty:
            xml = ''.join((xml, '/>\n'))
        else:
            xml = ''.join((xml, '>\n' + content + '</{}>\n'.format(tag)))

        if indent:
            spaces = ' ' * indent
            return spaces + xml.replace('\n', '\n' + spaces).rstrip(' ')
        else:
            return xml

    return to_xml
