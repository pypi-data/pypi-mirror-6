# -*- coding: UTF-8 -*-

"""
This module provides a way to manage a configuration from multiple sources with
an unique method to get it.

Use ``Config()`` for a custom configuration. ``default`` is provided to be used
as a global configuration.
"""

__version__ = '0.0.1'

import os


class Config():
    """
    Represent a configuration. This class should be use with dict-like getters
    and setters, e.g.:
        conf = Config()
        conf['bar'] = 42
        print conf['foo']
        print conf['bar']
    """

    def __init__(self, config={}, defaults={}, sources=[]):
        """
        Create a configuration. Initial values can be given using the
        ``config`` optional keyword argument. By default, it'll fallback on
        environment variables. A custom list of sources can be provided with
        the ``sources`` optional keyword argument.
        """
        self._config = config
        self._sources = sources
        self._defaults = defaults
        if os.environ not in self._sources:
            sources.append(os.environ)
        if self._config not in self._sources:
            self._sources.insert(0, self._config)

        self._sources.append(self._defaults)

    def __getitem__(self, key):
        """
        Get a key from this configuration. Each source is tested for the key
        and the first available value is returned. If no source contains this
        key, ``None`` is returned.
        """
        for source in self._sources:
            if key in source:
                return source[key]

    def __setitem__(self, key, value):
        """
        Set a key in this configuration
        """
        self._config[key] = value

    def setdefault(self, key, value):
        """
        Set a default value for a key
        """
        self._defaults[key] = value

# export a default config that can be used globally
default = Config()
