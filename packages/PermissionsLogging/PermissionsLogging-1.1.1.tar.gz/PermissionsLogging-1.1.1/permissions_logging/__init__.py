"""
A collection of log handlers that allow file permissions to be specified.
"""
import logging
import logging.handlers as handlers
import os


class FileHandler(logging.FileHandler):
    """
    A subclass of logging.FileHandler that accepts a permissions argument.

    The file used for logging will have the value of the permissions keyword
    value, e.g. for unix:  permissions=0o664
    """
    def __init__(self, filename, permissions=0o644):
        self.permissions = permissions
        logging.FileHandler.__init__(self, filename, **kwargs)

    def _open(self):
        stream = logging.FileHandler._open(self)
        try:
            os.chmod(self.baseFilename, self.permissions)
        except OSError as ex:
            # If we don't have access to change the permissions, we need to
            # rely on the initial file creator having done the chmod
            pass

        return stream


class TimedRotatingFileHandler(FileHandler, handlers.TimedRotatingFileHandler):
    """
    A subclass of logging.handlers.TimedRotatingFileHandler that accepts
    a permissions argument.

    The file used for logging will have the value of the permissions keyword
    value, e.g. for unix:  permissions=0o664
    """
    def __init__(self, filename, permissions=0o644, **kwargs):
        self.permissions = permissions
        handlers.TimedRotatingFileHandler.__init__(self, filename, **kwargs)


class WatchedFileHandler(FileHandler, handlers.WatchedFileHandler):
    """
    A subclass of logging.handlers.WatchedFileHandler that accepts
    a permissions argument.

    The file used for logging will have the value of the permissions keyword
    value, e.g. for unix:  permissions=0o664
    """
    def __init__(self, filename, permissions=0o644, **kwargs):
        self.permissions = permissions
        handlers.WatchedFileHandler.__init__(self, filename, **kwargs)


class RotatingFileHandler(FileHandler, handlers.RotatingFileHandler):
    """
    A subclass of logging.handlers.RotatingFileHandler that accepts
    a permissions argument.

    The file used for logging will have the value of the permissions keyword
    value, e.g. for unix:  permissions=0o664
    """
    def __init__(self, filename, permissions=0o644, **kwargs):
        self.permissions = permissions
        handlers.RotatingFileHandler.__init__(self, filename, **kwargs)
