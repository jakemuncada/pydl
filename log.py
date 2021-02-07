import os
import logging
from logging.handlers import RotatingFileHandler


class LogSettings:
    """
    Handles the initialization and settings of the logger.
    """

    # The root logger.
    _rootLogger = logging.getLogger()

    # The handler that prints messages to the log file.
    _fileHandler = None

    # The handler that displays messages on the console.
    _consoleHandler = None

    # The list of all loggers that this app uses.
    LOGGERS = ['__main__', 'settings', 'pydlr']

    @staticmethod
    def init():
        """
        Initialize the logger.
        """
        LogSettings._rootLogger.setLevel(logging.DEBUG)

        # Manually set the library loggers level to WARNING
        logging.getLogger('urllib3').setLevel(logging.WARNING)
        logging.getLogger('chardet').setLevel(logging.WARNING)

        LogSettings._addFileHandler()
        LogSettings._addConsoleHandler()

    @staticmethod
    def enableVerbose():
        """
        Enable verbose mode, which allows DEBUG messages to be displayed on the console.
        """
        if LogSettings._consoleHandler is None:
            LogSettings._consoleHandler = logging.StreamHandler()
        LogSettings._consoleHandler.setLevel(logging.DEBUG)

    @staticmethod
    def close():
        """
        Close the log.
        """
        if LogSettings._fileHandler is not None:
            LogSettings._fileHandler.close()
        if LogSettings._consoleHandler is not None:
            LogSettings._consoleHandler.close()

    @staticmethod
    def _addFileHandler():
        """
        Add the handler that prints messages to the log file.
        """
        # The maximum size of a log file
        MAX_BYTES = 1000000

        # The number of log files to keep
        BACKUP_COUNT = 10

        # Create the log directory
        os.makedirs('./logs', exist_ok=True)

        # Add the file logging handler
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        LogSettings._fileHandler = RotatingFileHandler('./logs/app.log', encoding='utf-8',
                                                       maxBytes=MAX_BYTES, backupCount=BACKUP_COUNT)
        LogSettings._fileHandler.setFormatter(formatter)
        LogSettings._rootLogger.addHandler(LogSettings._fileHandler)

    @staticmethod
    def _addConsoleHandler():
        """
        Add the handler that prints messages to the console.
        """
        LogSettings._consoleHandler = logging.StreamHandler()

        # Set formatter to print only the message in console
        formatter = logging.Formatter('%(message)s')
        LogSettings._consoleHandler.setFormatter(formatter)

        # Don't print exception trace in console
        filter = logging.Filter()
        filter.filter = lambda record: record.name in LogSettings.LOGGERS and not record.exc_info
        LogSettings._consoleHandler.addFilter(filter)

        # Initially set level to INFO
        LogSettings._consoleHandler.setLevel(logging.INFO)

        LogSettings._rootLogger.addHandler(LogSettings._consoleHandler)
