"""
SPADL - Sane Python adapter to DbgLog

Allows to log using standard Python logging to DbgLog
(http://dbglog.sourceforge.net/).

"""

import logging

from dbglog import dbg


DEBUG = 'DBG'
INFO = 'INFO'
WARNING = 'WARN'
ERROR = 'ERR'
FATAL = 'FATAL'

DBG_LOG_LEVELS = {
    logging.DEBUG: DEBUG,
    logging.INFO: INFO,
    logging.WARNING: WARNING,
    logging.ERROR: ERROR,
    logging.FATAL: FATAL,
}

# Default format
# It contains only information which is not present in DbgLog output.
BASIC_FORMAT = '%(name)s: %(message)s'


def configure(severity=1, level=None, format=BASIC_FORMAT, datefmt=None):
    """
    Configure Python logging to write to DbgLog.

    This function adds a configured `DbgLogHandler` to the root logger.
    It can be used as a shortcut in common cases when detailed
    configuration is not necessary.

    Note that this method does not configure DbgLog itself.

    :param severity: int or dict, for the `DbgLogHandler` constructor
    :param level: sets level of the root logger if not None
    :param format: given to the handler's formatter
    :param datefmt: given to the handler's formatter

    """
    handler = DbgLogHandler(severity)
    formatter = logging.Formatter(format, datefmt)
    handler.setFormatter(formatter)
    root = logging.getLogger()
    root.addHandler(handler)
    if level is not None:
        root.setLevel(level)


class DbgLogHandler(logging.Handler):
    """
    A handler class which writes logging records to DbgLog.

    :param severity: A dictionary mapping logger names to severities
            (numbers 1-4 inclusive, use 0 for ignoring specific logger).
            Alternatively an integer number can be given and it will
            be used as default severity for all loggers.

    """

    def __init__(self, severity):
        logging.Handler.__init__(self)
        if isinstance(severity, (int, long)):
            self.severities = {'': severity}
        else:
            self.severities = severity

    def emit(self, record):
        """
        Emits a record.

        Logs the record using the DbgLog library.

        """
        try:
            severity = self.getDbgLogSeverity(record)
            if not severity > 0:
                return
            level = self.getDbgLogLevel(record)
            if not level > 0:
                return
            kwargs = {level: severity}
            # Do not format message if it wont be logged.
            if not dbg.checkLevel(**kwargs):
                return
            # The message is already formated, prevent formatting by DbgLog
            msg = self.format(record).replace('%', '%%')
            location = (record.filename, record.funcName, record.lineno)
            dbg.log(msg, location=location, **kwargs)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)

    def getDbgLogLevel(self, record):
        """
        Returns name of DbgLog level.

        Maps a standard logging level set to a `logging.LogRecord`
        instance to one of 'FATAL', 'ERR', 'WARN', 'INFO' and 'DBG'.

        """
        level = record.levelno
        try:
            return DBG_LOG_LEVELS[level // 10 * 10]
        except KeyError:
            return FATAL if level > logging.FATAL else 0

    def getDbgLogSeverity(self, record):
        """
        Returns severity for DbgLog.

        Maps a logger name set to a `logging.LogRecord` instance
        to a severity number from 1 to 4 (inclusive).

        """
        severities = self.severities
        name = record.name or 'root'
        try:
            return severities[name]
        except KeyError:
            pass
        prefix = name
        while prefix:
            try:
                prefix = prefix[:prefix.rindex('.')]
            except ValueError:
                prefix = ''
            try:
                severity = severities[prefix]
            except KeyError:
                continue
            else:
                severities[name] = severity
                return severity
        return 0
