# encoding: utf-8
"""
config - feed logging configurations represented in more hierarchical way
"""
__author__ = "Volodymyr Vitvitskyi"
__copyright__ = "Copyright 2013, River Meadow Software"
__email__ = "vvitvitskiy@rivermeadow.com"

# standard imports
from itertools import ifilterfalse, imap, izip


def load_config(configuration):
    """
    Load logging (configuration), declared in a hierarchical manner
    @type configuration: dict

    In the following example every logger has own section of loggers, using the
    same key "loggers".
    As a result of parsing configuration below such loggers will be configured

        - A
        - A.B
        - A.B.C
        - A.B.D

    Content of ``/etc/logging.yaml``, as an example of such configuration,
    but any other configuration type can be used to represent hierarchy
    or loggers.

        version: 1
        formatters:
                ...
        handlers:
                ...
        loggers:
                A:
                    handlers: ...
                    level: ...
                    propagate: <Bool>
                    loggers:
                        B:
                            handlers: ...
                            level: ...
                            propagate: <Bool>
                            loggers:
                                C:
                                    handlers: ...
                                    level: ...
                                    propagate: <Bool>
                                D:
                                    handlers: ...
                                    level: ...
                                    propagate: <Bool>

    """
    result = _except_of_loggers(configuration)
    result.update({"loggers": dict(
        _flatten_loggers(configuration.get("loggers")))})
    return result


def select_keys(dict_, keys):
    """
    Extract sub-dictionary from (dict_) by specified (keys).
    @type dict_: dict
    @type keys: iterable
    @rtype: dict
    @return: new copy of the dictionary with only specified (keys)
    """
    return dict(izip(keys, imap(dict_.get, keys)))


def _except_of_loggers(dict_):
    """
    Extract sub-dictionary from (dict_) except of "loggers" key
    @type dict_: dict
    @rtype: dict
    @return: new copy of the dictionary without "loggers" key
    """
    keys = tuple(ifilterfalse("loggers".__eq__, dict_))
    return select_keys(dict_, keys)


def _flatten_loggers(loggers_dict, parent_name=''):
    """
    Convert hierarchy of loggers to the flat representation used by
    logging.config moduler.

    @type loggers_dict: dict
    @type parent_name: str
    @return: list of flattened definitions for loggers
    @rtype: list[dict]
    """
    loggers = []
    for name, logger_dict in loggers_dict.iteritems():
        name = '.'.join(filter(bool, (parent_name, name)))
        loggers.append((name, _except_of_loggers(logger_dict)))
        children_dict = logger_dict.get('loggers', {})
        loggers.extend(_flatten_loggers(children_dict, name))
    return loggers
