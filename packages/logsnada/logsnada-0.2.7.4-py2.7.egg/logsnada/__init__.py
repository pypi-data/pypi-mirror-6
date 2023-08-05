# encoding: utf-8
"""
logsnada - python logging wrapper to define pattern-based names for loggers

Current logging mechanism allows to define logging configuration using only
constant values as a logger names. For the every defined constant value logging
will create singleton object on demand.

This module intended to make it possible define pattern of logger name in the
configuration so in the runtime it will be used and applied to all loggers
that match the pattern.

The first attempt to bring more dynamic nature in loggers name is to support
UUID as a part of name. For instance,

``a.b.c.<UUID>`` as a logger name will match logger with name:

    - a.b.c.d749680b-f2a9-46ea-aeb1-ebdd263bbb1a
    - a.b.c.d749680b-f2a9-46ea-aeb1-ebdd263bbb1a.d
    - a.b.c.d749680b-f2a9-46ea-aeb1-ebdd263bbb1a.d.e
"""
__author__ = "Volodymyr Vitvitskyi"
__copyright__ = "Copyright 2013, River Meadow Software"
__email__ = "vvitvitskiy@rivermeadow.com"


# standard imports
import logging


class CustomLogger(logging.Logger):
    """
    To bind all loggers with pattern logger used for the configuration,
    logging has to use this class which has a reference to pattern logger
    """

    # The pattern logger
    _pattern = None

    @property
    def pattern_logger(self):
        return self._pattern

    @pattern_logger.setter
    def pattern_logger(self, logger):
        self._pattern = logger

    def makeRecord(self, *args, **kwargs):
        """
        Wrap every record with information about logger name
        @rtype: Record
        """
        record = super(CustomLogger, self).makeRecord(*args, **kwargs)
        record.logger_name = self.name
        return record

    def __str__(self):
        return 'CustomerLogger({}, {})'.format(self.propagate, self.level)


class PatternComposer(object):
    """
    Composer knows how to pack logger name to the one with pattern in it
    """

    def __init__(self, keyword):
        '''
        @param keyword: simple string keyword used as a pattern in the logger
                        name definitions
        @type keyword: str
        '''
        self.__keyword = keyword

    def compose(self, logger):
        """
        Compose pattern which is a packed logger name to use (keyword).

        For instance, if passed logger name is ``A.B.C``
        and keyword is '<L>' the result will be ``A.B.<L>``.

        The behaviour differs when (logger) is an instance of CustomerLogger.
        In this case we try to use pattern_logger in the name composition.

        @type logger: logging.Logger
        @rtype: str
        @return: logger name packed as a name with pattern or None
        """
        if not logger.name.endswith(self.__keyword):
            parent = logger.parent
            if (isinstance(parent, CustomLogger)
                and parent.pattern_logger):
                pattern = parent.pattern_logger.name
            else:
                pattern = take_parent_name(logger.name)
            return '.'.join((pattern, self.__keyword))


class CustomManager(object):
    """
    Wrapper for the logging.Manager that redefines behavior of getting loggers
    by name. In this part we match asked logger name against registered
    patterns
    """
    def __init__(self, manager, pattern_composer):
        """
        @type manager: logging.Manager
        @type pattern_composer: PatternComposer
        """
        self.wrapped = manager
        self.__root_logger = manager.root
        self.pattern_composer = pattern_composer

    def getLogger(self, name):
        """
        Get logger based on name
        @type name: str
        @rtype: logging.Logger
        """
        if name in self.loggerDict:
            return self.wrapped.getLogger(name)

        logger = self.wrapped.getLogger(name)
        pattern = self.pattern_composer.compose(logger)
        if pattern in self.loggerDict:
            logger_def = self.wrapped.getLogger(pattern)
            self.__update_logger(logger, logger_def)
        elif (isinstance(logger.parent, CustomLogger)
              and logger.parent.pattern_logger):
            short_name = logger.name[logger.name.rfind('.'):]
            pattern = logger.parent.pattern_logger.name + short_name
            if pattern in self.loggerDict:
                logger_def = self.wrapped.getLogger(pattern)
                self.__update_logger(logger, logger_def)
        return logger

    @classmethod
    def __update_logger(cls, logger, logger_def):
        """
        Update newly created logger with found pattern logger
        """
        logger.level = logger_def.level
        map(logger.addHandler, filter(bool, logger_def.handlers))
        map(logger.addFilter, filter(bool, logger_def.filters))
        logger.propagate = logger_def.propagate
        logger.pattern_logger = logger_def

    def __getattr__(self, name):
        return getattr(self.wrapped, name)


def take_parent_name(name):
    """
    Take substring from (name) which represents parent in hierarchy
    declared using dotted notation

    >>> take_parent_name('a.b.c')
    'a.b'
    >>> take_parent_name('a')
    ''
    >>> take_parent_name('')
    ''

    @type name: str
    @rtype: str
    """
    return name[:name.rfind('.')]


def init(composer):
    logging.setLoggerClass(CustomLogger)
    logging.Logger.manager = CustomManager(logging.Logger.manager, composer)
