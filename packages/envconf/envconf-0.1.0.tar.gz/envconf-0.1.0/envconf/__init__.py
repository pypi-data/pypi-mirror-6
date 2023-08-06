# -*- coding: UTF-8 -*-

"""
This module provides a way to manage a configuration from multiple sources with
an unique method to get it.

.. moduleauthor:: Baptiste Fontaine <b@ptistefontaine.fr>
"""

__version__ = '0.1.0'

import os


class Config():
    """
    Represent a configuration. This class should be use with dict-like getters
    and setters.

    >>> from envconf import Config
    >>> myconf = Config()
    >>> print myconf['HOME']
    /home/you
    >>> myconf['foo'] = 42
    >>> print myconf['foo']
    42
    >>> print repr(myconf['nothing'])
    None

    The configuration uses a list of possible sources for config values, and
    return the first matching value. If no value is available, ``None`` is
    returned.

    Keyword arguments:
            - ``config`` (``dict``): initial values. They override values from
              other sources.
            - ``defaults`` (``dict``): default values. These are used as the
              last source.
            - ``sources`` (``list``): override the sources list. This should be
              a list of dictionnaries that'll be used to get the configuration
              values. It'll be appended with ``os.environ`` and ``defaults``,
              and prepended with ``config``.
    """

    def __init__(self, config=None, defaults=None, sources=None):
        self._sources = sources[:] if sources else []

        self._sources.insert(0, config or {})
        self._sources.append(os.environ)
        self._sources.append(defaults or {})

    def __getitem__(self, key):
        """Get a key from this configuration."""
        for source in self._sources:
            if key in source:
                return source[key]

    def __setitem__(self, key, value):
        """Set a key in this configuration"""
        self._config[key] = value

    def __delitem__(self, key):
        """
        Delete a key in the explicit configuration source.

        .. versionadded:: 0.1.0
        """
        del self._config[key]

    @property
    def _config(self):
        return self._sources[0]

    def setdefault(self, key, value):
        """
        Set a default value for a key.

        >>> from envconf import Config
        >>> myconf = Config()
        >>> myconf.setdefault('foo', 'bar')
        >>> myconf['foo'] = 'barrr'
        >>> print myconf['foo']
        barrr
        >>> del myconf['foo']
        >>> print myconf['foo']
        bar
        """
        self._sources[-1][key] = value

default = Config()
"""
This is a default empty configuration that can be used to provide a global
configuration for all modules that import ``envconf``.

>>> import envconf
>>> envconf.default['foo'] = 17
>>> print envconf.default['foo']
17
"""
