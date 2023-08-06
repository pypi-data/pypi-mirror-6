#-*- coding: utf-8 -*-
#
# Copyright © 2014 Jean des Morts <jean.des.morts@gmail.com>
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To Public License, Version 2,
# as published by Sam Hocevar. See the COPYING.WTFPL file for more details.

__author__ = 'jdmorts'

import logging

from ail.util import AuthenticationError, make_to_xml

logger = logging.getLogger(__name__)


class Credential(object):
    """
    """
    def __init__(self, usernames=tuple(), passwords=tuple(), keys=tuple()):
        self._usernames = usernames
        self._passwords = passwords
        self._keys = keys

    @property
    def usernames(self):
        return self._usernames

    @property
    def passwords(self):
        return self._passwords

    @property
    def keys(self):
        return self._keys


class Profile(object):
    """The base class for all service profiles.

    A Profile is essentially an adaptor for a Service, thus insulating Platforms
    from the means by which they retrieve data. As conceived, the mapping of
    Profiles to Services for a particular operation is one-to-one:
    ::
     .---------------------.
     | _execute_profiles() | Platform
     '-------|----^--------'
      .------v----|-------.
      |     execute()     |
      |     v      ^      |  Profile
      | _input   _parse() |
      '----|--------^-----'
      .----v--------|-----.
      |  send()-->output  |  Service
      '-------------------'
    """
    service = None
    svc_params = {}

    def __repr__(self):
        return ''.join('{:s} ({:s})'.format(self, self._input))

    def __str__(self):
        return self.__class__.__name__

    @property
    def _input(self):
        raise NotImplementedError("Method '_parse' not implemented!")

    @staticmethod
    def _parse(output):
        raise NotImplementedError("Method '_parse' not implemented!")

    def execute(self, service):
        try:
            service.send(self._input)
            return self._parse(service.output)

        except (IOError, ValueError):
            raise


class Service(object):
    """
    """
    def __init__(self, credential, address):
        """Base class for all service classes.

        :param credential: an instance of the :class:`Credential` class
        :type credential: instance of :class:`Credential`
        :param address: platform location
        :type address: str
        """
        assert isinstance(credential, Credential)

        self._credential = credential
        self._address = address
        self._output = None
        self._errout = None

    @property
    def output(self):
        return self._output

    @property
    def errout(self):
        return self._errout


class CachedOperation(object):
    """This is a decorator that returns old results when the caller doesn't care
    about new ones. Cached data never becomes 'stale'.
    """
    def __init__(self, func):
        """Initialize new CachedOperation decorator.

        :param func: decorated function or method
        :type func: function
        """
        self._op = func
        self._cache = {}  # Storage for cached output
        self._instance = None
        self._owner = None

    def __call__(self, *args, **kwargs):
        key = ''.join(args)

        # if not kwargs.pop('refresh', False):
        #     try:
        #         return self._cache[key]
        #
        #     except KeyError:
        #         pass

        if callable(self._op):
            result = self._op.__call__(*args, **kwargs)
        else:
            result = self._op.__get__(self._instance, self._owner)

        self._cache[key] = result

        return result

    def __get__(self, instance, owner):
        if not instance:
            return self

        self._instance = instance
        self._owner = owner

        return self.__call__()


class Platform(object):
    """
    """
    def __init__(self, platform_type, address):
        """Create a platform instance.

        :param platform_type: subclass description
        :type platform_type: str
        :param address: location of platform
        :type address: str
        """
        self._type = platform_type
        self._address = address
        self._credentials = []  # Stores the credential chain
        self._services = {}  # Cache for service modules

    def _execute_profiles(self, *profiles):
        """
        """
        for profile in profiles:
            for credential in self._credentials:
                try:
                    # Check cache for a service matching this profile
                    service = self._services[str(profile)]

                except KeyError:
                    try:
                        try:
                            params = profile.svc_params

                        except AttributeError:
                            params = {}

                        service = profile.service(credential, self._address,
                                                  **params)

                    except AuthenticationError as e:
                        # Proceed to the next credential if authentication fails
                        logger.warn(('Authentication failure in platform {}, ' +
                                     'address {}: {:s}').format(self._type,
                                                                self._address,
                                                                e))
                        continue

                    except IOError as e:
                        # Proceed to next profile if unable to connect
                        logger.error(('Connection failure in platform {}, ' +
                                      'address {}: {:s}').format(self._address,
                                                                 type(e), e))
                        break

                    except AttributeError:
                        # Proceed to next profile if .service is undefined
                        logger.error(('Undefined service attribute for ' +
                                      'profile {}').format(repr(profile)))
                        break
                    # Cache the resulting service instance
                    self._services[str(profile)] = service

                try:
                    return profile.execute(service)

                except IOError as e:
                    # If we failed to send input or receive output,
                    logger.warn('I/O error in platform {}, address {}: {:s}'.
                                format(self._type, self._address, e))

                except ValueError as e:
                    # If the service output was unexpected,
                    logger.error('Value error in platform {}, address {}: {:s}'.
                                 format(self._type, self._address, e))

                except NotImplementedError as e:
                    # If this profile lacks an important method
                    logger.error('Missing interface in profile {}: {:s}'.
                                 format(repr(profile), e))

                except Exception as e:
                    # Protect ourselves from errant profiles
                    logger.error(('Unhandled exception in platform {}, ' +
                                  'address {}, while executing profile ' +
                                  '{}: {:s}').
                                 format(self.type, profile, e))
            # Having failed to authenticate using any of the given credentials,
            logger.warn(('Exhausted credential chain in platform {}, address ' +
                         '{}, for profile {:s}').format(self._type,
                                                        self._address,
                                                        profile))
        # When none of the given profiles yield a result,
        raise IOError('Exhausted all profiles for operation on address {}'.
                      format(self._address))

    @property
    def address(self):
        return self._address

    @property
    def credentials(self):
        """Return the stored credential chain.

        :return: credential chain used for service authentication
        :rtype: seq of Credential()
        """
        return self._credentials

    @credentials.setter
    def credentials(self, credentials):
        """Set the credential chain.

        :param credentials: credential chain used for service authentication
        :type: seq of Credential()
        """
        for c in credentials:
            if not isinstance(c, Credential):
                raise TypeError("Expected type 'Credential'; got {:s} instead".
                                format(c))

        self._credentials = credentials

    @property
    def type(self):
        return self._type


class IterablePlatform(Platform):
    def __init__(self, platform_type, address):
        super(IterablePlatform, self).__init__(platform_type, address)
        self._to_xml = make_to_xml(())

    def __iter__(self):
        """Iterate only those attributes decorated with @CachedOperation.
        """
        for k, v in sorted(self.__class__.__dict__.items(), key=lambda i: i[0]):
            if isinstance(v, CachedOperation):
                yield k

    def prefetch(self):
        """Pre-cache results for all cache-able operations.
        """
        for op in self:
            logger.info("{}: fetching op '{:s}'".format(self._address, op))
            op()

    def to_xml(self, empty=False, indent=0, tag='platform'):
        """Generate XML for all operations with @CachedOperation decorator.

        :param empty: when true, try to make empty element ('/>')
        :type empty: bool
        :param indent: indents the resulting output by 'indent' spaces
        :type indent: int
        :param tag: overrides the default tag of self.__class__.__name__
        :type tag: str

        :return: resulting XML
        :rtype: str
        """
        results = []

        for op in self:
            try:
                results.append(getattr(self, op))

            except IOError:
                continue

        return self._to_xml(self, results, indent=indent, tag=tag)
