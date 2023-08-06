"""
Errors to be used by PyChromecast.
"""


class PyChromecastError(Exception):
    """ Base error for PyChromecast. """
    pass


class NoChromecastFoundError(PyChromecastError):
    """
    When a command has to auto-discover a Chromecast and cannot find one.
    """
    pass


class ConnectionError(PyChromecastError):
    """ When a connection error occurs within PyChromecast. """
    pass
