
import re
import os
import errno
import logging
import tempfile
import unittest

from dbglog import dbg

import spadl


class DbgLogHandlerTestCase(unittest.TestCase):
    """
    Tests for the the `DbgLogHandler` class.
    """

    def setUp(self):
        # Configure Python logging
        logger = logging.getLogger()
        self.origLevel, logger.level = logger.level, logging.NOTSET
        self.handlers = []
        # Configure DbgLog
        self.origLogMask = dbg.getLogMask()
        dbg.logMask('F1E1W1I1D1')
        self.origLogFile = dbg.getLogFile()
        self.filename = tempfile.mktemp(suffix='.log')
        dbg.logFile(self.filename)

    def tearDown(self):
        # Restore Python logging configuration
        logger = logging.getLogger()
        logger.level = self.origLevel
        for handler in self.handlers:
            logger.removeHandler(handler)
        # Restore DbgLog configuration
        dbg.logMask(self.origLogMask)
        dbg.logFile(self.origLogFile or '')
        try:
            os.remove(self.filename)
        except EnvironmentError:
            pass

    def addHandler(self, severity=1):
        handler = spadl.DbgLogHandler(severity)
        logging.getLogger().addHandler(handler)
        self.handlers.append(handler)

    def readLogFile(self):
        try:
            with open(self.filename, 'rb') as f:
                return f.read()
        except EnvironmentError as e:
            if e.errno == errno.ENOENT:
                return ''
            raise

    def getMessagePattern(self, message, level=None):
        if level is None:
            return '%s.* {%s' % (message, __file__)
        return '%s:.* %s.* {%s' % (level, message, __file__)

    def assertLogMessage(self, message, level=None):
        content = self.readLogFile()
        pattern = self.getMessagePattern(message, level)
        self.assertTrue(re.search(pattern, content),
                        'Message %r was not found in log.' % message)


    def assertNoLogMessage(self, message, level=None):
        content = self.readLogFile()
        pattern = self.getMessagePattern(message, level)
        self.assertFalse(re.search(pattern, content),
                         'Message %r was found in log.' % message)

    def testDebugIsLogged(self):
        self.addHandler()
        logging.debug('Example debug message')
        self.assertLogMessage('Example debug message', 'D1')

    def testInfoIsLogged(self):
        self.addHandler()
        logging.info('Example info message')
        self.assertLogMessage('Example info message', 'I1')

    def testWarningIsLogged(self):
        self.addHandler()
        logging.warning('Example warning message')
        self.assertLogMessage('Example warning message', 'W1')

    def testErrorIsLogged(self):
        self.addHandler()
        logging.error('Example error message')
        self.assertLogMessage('Example error message', 'E1')

    def testFatalIsLogged(self):
        self.addHandler()
        logging.fatal('Example fatal message')
        self.assertLogMessage('Example fatal message', 'F1')

    def testNegativeLevelIsNotLogged(self):
        self.addHandler()
        logging.log(-1, 'Example message')
        self.assertNoLogMessage('Example message')

    def testZeroLevelIsNotLogged(self):
        self.addHandler()
        logging.log(0, 'Example message')
        self.assertNoLogMessage('Example message')

    def testLevelUnderDebugNotIsLogged(self):
        self.addHandler()
        logging.log(logging.DEBUG - 1, 'Example message')
        self.assertNoLogMessage('Example message')

    def testLevelOverDebugIsLogged(self):
        self.addHandler()
        logging.log(logging.DEBUG + 1, 'Example message')
        self.assertLogMessage('Example message', 'D1')

    def testLevelUnderInfoIsLogged(self):
        self.addHandler()
        logging.log(logging.INFO - 1, 'Example message')
        self.assertLogMessage('Example message', 'D1')

    def testLevelOverInfoIsLogged(self):
        self.addHandler()
        logging.log(logging.INFO + 1, 'Example message')
        self.assertLogMessage('Example message', 'I1')

    def testLevelUnderWarningIsLogged(self):
        self.addHandler()
        logging.log(logging.WARNING - 1, 'Example message')
        self.assertLogMessage('Example message', 'I1')

    def testLevelOverWarningIsLogged(self):
        self.addHandler()
        logging.log(logging.WARNING + 1, 'Example message')
        self.assertLogMessage('Example message', 'W1')

    def testLevelUnderErrorIsLogged(self):
        self.addHandler()
        logging.log(logging.ERROR - 1, 'Example message')
        self.assertLogMessage('Example message', 'W1')

    def testLevelOverErrorIsLogged(self):
        self.addHandler()
        logging.log(logging.ERROR + 1, 'Example message')
        self.assertLogMessage('Example message', 'E1')

    def testLevelUnderFatalIsLogged(self):
        self.addHandler()
        logging.log(logging.FATAL - 1, 'Example message')
        self.assertLogMessage('Example message', 'E1')

    def testLevelOverFatalIsLogged(self):
        self.addHandler()
        logging.log(logging.FATAL + 1, 'Example message')
        self.assertLogMessage('Example message', 'F1')

    def testHugeLevelIsLogged(self):
        self.addHandler()
        logging.log(100, 'Example message')
        self.assertLogMessage('Example message', 'F1')

    def testRootLoggerWithZeroSeverity(self):
        self.addHandler(0)
        logging.debug('Example message')
        self.assertNoLogMessage('Example message')

    def testRootLoggerWithSeverityEqualToOne(self):
        self.addHandler(1)
        logging.debug('Example message')
        self.assertLogMessage('Example message', 'D1')

    def testRootLoggerWithSeverityEqualToTwo(self):
        self.addHandler(2)
        logging.info('Example message')
        self.assertLogMessage('Example message', 'I2')

    def testRootLoggerWithSeverityEqualToThree(self):
        self.addHandler(3)
        logging.warning('Example message')
        self.assertLogMessage('Example message', 'W3')

    def testRootLoggerWithSeverityEqualToFour(self):
        self.addHandler(4)
        logging.error('Example message')
        self.assertLogMessage('Example message', 'E4')

    def testCustomLoggerWithZeroSeverity(self):
        self.addHandler(0)
        logging.getLogger('foo.bar').debug('Example message')
        self.assertNoLogMessage('Example message')

    def testCustomLoggerWithSeverityEqualToOne(self):
        self.addHandler(1)
        logging.getLogger('foo.bar').debug('Example message')
        self.assertLogMessage('Example message', 'D1')

    def testCustomLoggerWithSeverityEqualToTwo(self):
        self.addHandler(2)
        logging.getLogger('foo.bar').info('Example message')
        self.assertLogMessage('Example message', 'I2')

    def testCustomLoggerWithSeverityEqualToThree(self):
        self.addHandler(3)
        logging.getLogger('foo.bar').warning('Example message')
        self.assertLogMessage('Example message', 'W3')

    def testCustomLoggerWithSeverityEqualToFour(self):
        self.addHandler(4)
        logging.getLogger('foo.bar').error('Example message')
        self.assertLogMessage('Example message', 'E4')

    def testRootLoggerWithoutRootSeverity(self):
        self.addHandler({})
        logging.info('Example message')
        self.assertNoLogMessage('Example message')

    def testRootLoggerWithRootSeverity(self):
        self.addHandler({'': 4})
        logging.info('Example message')
        self.assertLogMessage('Example message', 'I4')

    def testCustomLoggerWithoutRootSeverity(self):
        self.addHandler({})
        logging.getLogger('foo.bar').info('Example message')
        self.assertNoLogMessage('Example message')

    def testCustomLoggerWithRootSeverity(self):
        self.addHandler({'': 4})
        logging.getLogger('foo.bar').info('Example message')
        self.assertLogMessage('Example message', 'I4')

    def testSeverityFromGivenLoggerIsUsed(self):
        self.addHandler({'foo.bar': 4, 'foo': 3, '': 2})
        logging.getLogger('foo.bar').info('Example message')
        self.assertLogMessage('Example message', 'I4')

    def testSeverityFromParentLoggerIsUsed(self):
        self.addHandler({'foo.bar': 4, 'foo': 3, '': 2})
        logging.getLogger('foo.baz').info('Example message')
        self.assertLogMessage('Example message', 'I3')

    def testSeverityFromRootLoggerIsUsed(self):
        self.addHandler({'foo.bar': 4, 'foo': 3, '': 2})
        logging.getLogger('baz.bar').info('Example message')
        self.assertLogMessage('Example message', 'I2')

    def testSeverityFromSimilarLoggerIsNotUsed(self):
        self.addHandler({'foo.bar': 4, 'foo': 3, '': 2})
        logging.getLogger('foooo').info('Example message')
        self.assertLogMessage('Example message', 'I2')

    def testMessageWithParams(self):
        self.addHandler()
        logging.info('"%s %s"', 'hello', 'world')
        self.assertLogMessage('"hello world"')

    def testMessageWithNamedParams(self):
        self.addHandler()
        logging.info('"%(h)s %(w)s"', {'h':'hello', 'w': 'world'})
        self.assertLogMessage('"hello world"')

    def testMessageWithPercentSign(self):
        self.addHandler()
        logging.info('"100%"')
        self.assertLogMessage('"100%"')

    def testMessageWithPercentSignAndParams(self):
        self.addHandler()
        logging.info('"100%% %s %s"', 'hello', 'world')
        self.assertLogMessage('"100% hello world"')

    def testMessageWithPercentSignAndNamedParams(self):
        self.addHandler()
        logging.info('"100%% %(h)s %(w)s"', {'h':'hello', 'w': 'world'})
        self.assertLogMessage('"100% hello world"')


if __name__ == '__main__':
    unittest.main()
