"""
Module for sending service logs to a UDP JSON collector.

Defines helper functions configure and log for global
use of the module within an application. A default
logger is always defined at module load time so in most
cases there is no configuring required, just import
the module and 'log'.

Also exposes the UDPLogger class which can be injected
in order to define mulitple loggers.

Finally, offers a JSONUDPHandler logging handler class to
route logging to a JSON UDP collector.
"""

import json
import logging
import logging.handlers
from socket import socket, AF_INET, SOCK_DGRAM


DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 9011

__logger = None


def log(packet):
    """
    >>> log({'msg': 'hello', 'pid': 45})
    """
    if __logger:
        __logger.log(packet)


def configure(host=DEFAULT_HOST, port=DEFAULT_PORT):
    """
    >>> configure('localhost', 9011)
    """
    global __logger
    __logger = UDPLogger(host, port)


class UDPLogger(object):
    "Logger class to send messages to a UDP socket"
    def __init__(self, host='localhost', port=9011):
        """
        >>> logger = UDPLogger()
        """
        self.addr = (host, port)

    def log(self, data):
        """
        Serialize data to JSON and send to collector.

        >>> logger = UDPLogger()
        >>> logger.log({'key': 'value'})
        >>> logger.log(object()) # doctest: +ELLIPSIS
        Traceback (most recent call last):
            ...
        TypeError: ...
        """
        self.send(json.dumps(data))

    def send(self, jsonstr):
        """
        Send jsonstr to the UDP collector

        >>> logger = UDPLogger()
        >>> logger.send('{"key": "value"}')
        """
        udp_sock = socket(AF_INET, SOCK_DGRAM)
        udp_sock.sendto(jsonstr.encode('utf-8'), self.addr)


# always have a default logger
configure()


# integration with standard logging
class JSONUDPHandler(logging.handlers.DatagramHandler):
    """
    Send log records as JSON UDP packets.

    Configure logging to use this handler, e.g.

    >>> logger = logging.getLogger('testing')
    >>> logger.propagate = False
    >>> logger.addHandler(JSONUDPHandler())
    >>> logger.critical('testing')
    """
    def __init__(self, host=DEFAULT_HOST, port=DEFAULT_PORT):
        super(JSONUDPHandler, self).__init__(host, port)

    def emit(self, record):
        try:
            jsonstr = self.to_json(record)
            self.send(jsonstr)
        except (KeyboardInterrupt, SystemExit): # pragma: no cover
            raise
        except: # pragma: no cover
            self.handleError(record)

    @staticmethod
    def to_json(record):
        "Serialize record to JSON"
        return json.dumps(record.__dict__, cls=SafeJSONEncoder)


class SafeJSONEncoder(json.JSONEncoder):
    """
    Catches default encoder's TypeErrors and use default object's
    string representation i.e. str(obj).

    >>> import datetime
    >>> json.dumps({1: datetime.datetime(2013, 12, 10)}, cls=SafeJSONEncoder)
    '{"1": "2013-12-10 00:00:00"}'
    """
    def default(self, obj):
        try:
            return super(SafeJSONEncoder, self).default(obj)
        except TypeError:
            return str(obj)
