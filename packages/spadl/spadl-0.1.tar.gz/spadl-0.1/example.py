
import logging

import spadl
from dbglog import dbg


# Configure Python logging
#
# The `spadl.configure` function can be used or the `spadl.DbgLogHandler`
# handler be created and registered using any method in the
# `logging.config` module.

spadl.configure({
    # Log records from the 'app' logger and its children will
    # be logged using the highest severity (D4, I4, W4, E4, F4).
    'app': 4,
    # But log records from the 'app.request' (and its children)
    # will be logged using a lower severity (D3, I3, W3, E3, F3).
    'app.request': 3,
    # Another severity for another loggers.
    'rpc': 2,
    # Log records from the 'db.sql' logger will be ignored.
    'db.sql': 0,
    # Specification of the default severity. If was not present here then
    # the default behaviour would be to ignore records from unknown loggers.
    '': 1,
}, level=logging.DEBUG)


# Configure DbgLog.
#
# Messages are written to error output for demonstration purposes
# but any DbgLog configuration is possible.
dbg.logStderr(True)
# It is a good idea to set a low DbgLog mask and filter records
# using standard logging levels. The effective logging levels can be
# easily checked using the `logging.Logger.isEnabledFor` method but
# testing DbgLog mask is insufficient if there are other logging handlers.
dbg.logMask('F1E1W1I1D1')


def demo():
    logging.debug('Hello world, this is logged as D1.')
    logging.getLogger('app.server').info('This application message is I4.')
    logging.getLogger('app.request').warning('But this message is W3.')
    logging.getLogger('rpc.stats').error('This is configured as E2.')
    logging.getLogger('db.connection').fatal('Level of this defaults to F1.')
    logging.getLogger('db.sql').debug('This is ignored and lost forever.')
    logging.log(25, 'Custom level is not a problem.')
    try:
        infinity = 1 / 0
    except ZeroDivisionError:
        logging.exception('Exceptions are logged too.')
    logging.getLogger('app').info('The last message must be %s!', 'GOOD')


if __name__ == '__main__':
    demo()
