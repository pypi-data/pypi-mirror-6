"""Logging core."""

__copyright__ = "Copyright (C) 2014 Ivan D Vasin"
__docformat__ = "restructuredtext"

import logging as _logging
from logging import *


INSECURE = 5
"""Insecure logging level.

Messages that contain sensitive data should be logged at or below this
level.

"""

_logging.addLevelName(INSECURE, 'INSECURE')


def cond(*args, **kwargs):
    getLogger().cond(*args, **kwargs)


def critical(*args, **kwargs):
    getLogger().critical(*args, **kwargs)


def debug(*args, **kwargs):
    getLogger().debug(*args, **kwargs)


def error(*args, **kwargs):
    getLogger().error(*args, **kwargs)


def getLogger(name=None):
    logger = _logging.getLogger(name)
    if isinstance(logger, Logger):
        return logger
    else:
        return LoggerWrapper(logger)


def info(*args, **kwargs):
    getLogger().info(*args, **kwargs)


def insecure(*args, **kwargs):
    getLogger().insecure(*args, **kwargs)


def log(*args, **kwargs):
    getLogger().log(*args, **kwargs)


def warning(*args, **kwargs):
    getLogger().warning(*args, **kwargs)


class Logger(_logging.Logger):

    def cond(self, *levels_factories):
        for level_factory in levels_factories:
            try:
                level, factory = level_factory
            except TypeError:
                raise TypeError('invalid (logging level, message factory) pair'
                                 ' {!r}'.format(level_factory))
            if self.isEnabledFor(level):
                self.log(level, factory())
                return

    def getChild(self, suffix):
        logger = super(Logger, self).getChild(suffix)
        if isinstance(logger, Logger):
            return logger
        else:
            return LoggerWrapper(logger)

    def insecure(self, *args, **kwargs):
        super(Logger, self).log(INSECURE, *args, **kwargs)


class LoggerWrapper(Logger):

    def __init__(self, logger):
        self.__dict__['_wrapped_logger'] = logger

    def __getattr__(self, name):
        return getattr(self._wrapped_logger, name)

    def __setattr__(self, name, value):
        setattr(self._wrapped_logger, name, value)
