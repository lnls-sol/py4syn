"""
    This module implements the Py4synLogger class.
"""
import logging
import os
import pwd
import pathlib


class Py4synLogger:
    """
        The Py4synLogger is a logger class that wraps the python logging library.
        Its purpose is to provide a simple and easy way of logging code execution
        in the context of the LNLS synchrotron.

        The Py4synLogger creates a Logger and 2 handlers for it, a RotatingFileHandler
        that writes any log with INFO level and above in a log file (by default this file is
        located in '$HOME/.local/var/log/' and its name is 'py4syn_logger.log', but this can
        be modified by the methods set_log_path and set_log_filename) and a StreamHandler
        that writes any log with WARNING level and above in the stdout.
    """
    def __init__(self, module_name, size_kb=512, backup_count=5):
        """
        **Constructor**

        Parameters
        ----------
        module_name : :obj:`string`
            Name of the module that is calling the Py4synLogger. Suggestion is to use
            __name__
        size_kb : :obj:`int`, optional
            Maximum size of the log file in kilobytes, by default 512
        backup_count : :obj:`int`, optional
            Maximum number of files that will be used to save previous logs, by default 5

        Examples
        ----------
        >>> logger = Py4synLogger(__name__, size_kb=64, backup_count=10)
        >>> logger.warning("A warning message!")
            [WARNING] - 2019-09-26 11:48:53,811 - py4syn_logger.package: A warning message!
        """
        self.module_name = module_name
        self.size_kb = size_kb
        self.backup_count = backup_count

        # Gets username that is executing the process, its home folder and
        # creates the default paths to the log file
        self.username = str(pwd.getpwuid(os.getuid())[0])
        self.user_home = os.path.expanduser('~' + self.username)

        # We chose the $HOME/.local as default path, because using this
        # path we avoid permission problems and also avoid possibility of users
        # seeing other users logs   
        self.log_path = pathlib.Path(self.user_home + '/.local/var/log')
        self.log_filename = 'py4syn_logger.log'

        if not self.log_path.is_dir():
            self.log_path.mkdir(parents=True)

        # Create the logger object
        self.logger = logging.getLogger('py4syn_logger' + '.' + self.module_name)
        self.logger.setLevel(logging.DEBUG)

        # Create file handler which logs INFO messages and above
        self.file_handler = logging.handlers.RotatingFileHandler(str(self.log_path / self.log_filename),
                                                                 maxBytes=1024*self.size_kb,
                                                                 backupCount=self.backup_count)
        self.file_handler.setLevel(logging.INFO)

        # Create console handler which logs WARN messages and above
        self.console_handler = logging.StreamHandler()
        self.console_handler.setLevel(logging.WARN)

        # Create formatter and add it to the handlers
        formatter = logging.Formatter('[%(levelname)s] - %(asctime)s - %(name)s: %(message)s')
        self.file_handler.setFormatter(formatter)
        self.console_handler.setFormatter(formatter)

        # Add the handlers to the logger object
        self.logger.addHandler(self.console_handler)
        self.logger.addHandler(self.file_handler)

    def debug(self, message):
        """
        Method to log DEBUG messages

        Parameters
        ----------
        message : :obj:`string`
            Message that will be logged
        """
        self._log(message, logging.DEBUG)

    def info(self, message):
        """
        Method to log INFO messages

        Parameters
        ----------
        message : :obj:`string`
            Message that will be logged
        """
        self._log(message, logging.INFO)

    def warning(self, message):
        """
        Method to log WARNING messages

        Parameters
        ----------
        message : :obj:`string`
            Message that will be logged
        """
        self._log(message, logging.WARNING)

    def error(self, message):
        """
        Method to log ERROR messages

        Parameters
        ----------
        message : :obj:`string`
            Message that will be logged
        """
        self._log(message, logging.ERROR)

    def _log(self, message, level):
        """
            Private method to pass message of specified level to the logger object

        Parameters
        ----------
        message : :obj:`string`
            Message that will be logged
        level : :obj:`int`
            Log level, avoid magic number, use logging levels enums.
        """
        self.logger.log(level, message)

    def _reload_file_handler(self, level=logging.INFO):
        """
            Private method to reload the file handler.
            When the log file path or name is chenged, this method should be
            called to reload the file handler with the new information.

        Parameters
        ----------
        level : :obj:`int`, optional
            Log level for the new file handler, by default logging.INFO
        """
        self.logger.removeHandler(self.file_handler)

        self.file_handler = logging.handlers.RotatingFileHandler(str(self.log_path / self.log_filename),
                                                                 maxBytes=1024*self.size_kb,
                                                                 backupCount=self.backup_count)
        self.file_handler.setLevel(level)

        self.logger.addHandler(self.console_handler)

    def set_log_path(self, path):
        """
            Set a new path to the log file.

        Parameters
        ----------
        path : :obj:`string`
            Absolute path to the directory that the log file will be written.
        """
        self.log_path = pathlib.Path(path)

        if not self.log_path.is_dir():
            self.log_path.mkdir(parents=True)

        self._reload_file_handler()

    def set_log_filename(self, filename):
        """
            Set a new filename to the log file.

        Parameters
        ----------
        filename : :obj:`string`
            Name of the log file.
        """
        self.log_filename = filename

        self._reload_file_handler()

    def set_filehandler_level(self, new_level):
        """
            Set a new log level to the file handler.

        Parameters
        ----------
        new_level : :obj:`int`
            New value of the file handler.
        """
        self.file_handler.setLevel(new_level)

    def set_console_level(self, new_level):
        """
            Set a new log level to the console handler.

        Parameters
        ----------
        new_level : :obj:`int`
            New value of the console handler.
        """
        self.console_handler.setLevel(new_level)
