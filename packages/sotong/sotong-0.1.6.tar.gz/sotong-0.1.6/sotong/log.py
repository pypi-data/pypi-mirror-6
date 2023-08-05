"""
Logging module

.. autosummary::

    JSONLogHandler
    get_logger
"""

import logging
import logging.handlers
import json


class JSONLogHandler(logging.handlers.RotatingFileHandler):
    def format(self, record):
        keys = ("created", "levelname", "pathname", "lineno", "msg", "args",
                "funcName", "exc_info")
        d = {}
        for key in keys:
            d[key] = _jsonize(getattr(record, key))
        return json.dumps(d)


def _jsonize(value):
    """ Jsonize value

    >>> _jsonize(123) + 1
    124
    >>> _jsonize('ABC')
    'ABC'
    >>> _jsonize([123, 'ABC', [1, 2, 3]])
    [123, 'ABC', [1, 2, 3]]
    >>> _jsonize({'a': 'AAA', 'b': 'BBB'})
    {'a': 'AAA', 'b': 'BBB'}
    >>> type(_jsonize(lambda x: x * 2))
    <type 'str'>
    """
    if type(value) in (str, int):
        return value 
    if type(value) in (list, tuple):
        try:
            json.dumps({'value': list(value)})
            return value
        except Exception as e:
            return str(value)
    try:
        json.dumps(value)
        return value
    except Exception as e:
        return str(value)


def get_logger():
    return logging.getLogger("sotong")

