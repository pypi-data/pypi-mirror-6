# encoding: utf-8
"""
handler - module defines handlers to be used with CustomLogger
"""

__author__ = "Volodymyr Vitvitskyi"
__copyright__ = "Copyright 2013, River Meadow Software"
__email__ = "vvitvitskiy@rivermeadow.com"

# standard imports
import os
import logging
from itertools import ifilterfalse
from logging.config import BaseConfigurator


class FileHandler(logging.FileHandler):
    """
    Takes care about creating non-existing directories specified
    in the (filename)
    """

    def __init__(self, filename, *args, **kwargs):
        """
        @type filename: str
        """
        path = _makedirs(filename)
        super(FileHandler, self).__init__(path, *args, **kwargs)


def _makedirs(path):
    """
    Create directories specified in (path) if they do not exist
    @type path: str
    @rtype: str
    @return: the same path as passed
    """
    file_dir = os.path.dirname(path)
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    return path


class LoggerNameBased(logging.FileHandler):
    """
    File handler manager that registers new file handler implementations of
    specified (fh_class).

    Registration of file handler is based on the logger name of LogRecord

    Records from the loggers with the same parent logger will be handled using
    the same handler instance.

    File handler instances are created based on (fh_class) provided and will
    write to the file with (filename). File itself is created in the directory
    with name of registered logger.

    In case if (dir_prefix) specified created directory name will be
    prefixed with it.

    Example below demonstrates how logging handled for different loggers

        a.b.c -> h1
        a.b.c.d -> h1
        a.b -> h2
        a.b.e -> h2

    Path composition of the log file consists of two configurable parts
    (dir_prefix), filename and logger name that appears in runtime only.

    The formula looks like the following:

        <dir_prefix><logger_name>/<filename>

    For instance:

        dir_prefix: '/var/logs/product/server_'
        filename: 'connections/core.log'

    The path to the file  with the logger 'LoggerName' that has such handler
    will be:

        /var/logs/product/server_LoggerName/connections/core.log
                                ^          ^
                                |          |
         ______________________/___________/
        /
        ^
        This is important: dir_prefix joined with logger name without slash,
            but logger name with filename using /
    """

    def __init__(self, fh_class, filename, dir_prefix=None,
                 mode='a', encoding=None):
        """
        @param fh_class: used to create handler per logger
        @type: logging.FileHandler
        @param filename: file with such name will be created
        """
        # set deploy value to truth to delay file opening
        delay = 1
        logging.FileHandler.__init__(self, filename, mode, encoding, delay)
        self.__filename = filename
        self.__dir_prefix = dir_prefix or ''
        self.__handler_by_logger = {}

        fh_class = (isinstance(fh_class, basestring)
                 and BaseConfigurator({}).resolve(fh_class)
                 or fh_class)
        assert issubclass(fh_class, logging.FileHandler)
        self.__fh_class = fh_class

    def close(self):
        """
        Close all file handlers for all registered loggers
        """
        map(logging.FileHandler.close, self.__handler_by_logger.itervalues())

    @classmethod
    def _prepare_path(cls, logger_name, path_prefix, filename):
        """
        @param logger_name: Logger name
        @type logger_name: str
        @param path_prefix: Used to construct path and prefix for the
                            directory created by logger name
        @type path_prefix: str
        @param filename: relative path with log file name
        @return full path to the file for the stream for (logger_name)
        @rtype: str
        """
        full_path = os.path.join(
            path_prefix + logger_name.rsplit('.', 1)[-1],
            filename
        )

        dir_name = os.path.dirname(full_path)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        return full_path

    def _create_handler(self, logger_name):
        filename = self._prepare_path(
            logger_name, self.__dir_prefix, self.__filename
        )
        handler = self.__fh_class(filename, self.mode, self.encoding)
        handler.setFormatter(self.formatter)
        map(handler.addFilter, self.filters)
        return handler

    def emit(self, record):
        """
        @type: logging.LogRecord
        """
        logger_name = record.logger_name
        stored_loggers = reversed(sorted(self.__handler_by_logger))
        for key_ in ifilterfalse(logger_name.find, stored_loggers):
            handler = self.__handler_by_logger[key_]
            break
        else:
            handler = self._create_handler(logger_name)
            self.__handler_by_logger[logger_name] = handler
        handler.emit(record)