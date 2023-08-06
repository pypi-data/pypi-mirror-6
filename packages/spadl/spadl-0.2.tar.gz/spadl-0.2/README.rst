
SPADL - Sane Python adapter to DbgLog
=====================================

This package provides a standard logging handler which writes log
records to `DbgLog`_.

You are probably not interested in this library unless you are
working for Seznam.cz.

A `spadl.DbgLogHandler` class implemented in this package allows you to use
and write code that uses the standard Python logging and at the same
time utilize DbgLog.

.. _DbgLog: http://dbglog.sourceforge.net/


Installation
------------

SPADL can be installed using pip (or easy_install) from PYPI: ::

    $ pip install spadl

Alternatively you can download and extract tarball and install the package manually: ::

    $ python setup.py install

Placing the package somewhere on the PYTHONPATH should also work.


Example usage
-------------

DbgLog distinguish severities of log records with same level.
Message can be logged for example as D4 (important debug) or E1 (minor error).
So the `spadl.DbgLogHandler` maps logger names to these severities.

There is `spadl.configure` function defined which simplifies
logging configuration. So the basic usage can be similar to: ::

    import spadl
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
    })

    # Now use logging normally.
    logging.info('This will be recorded by DbgLog.')

Alternatively you can configure logging using the `logging.config` package.
A relevant section in a configuration file for the `logging.config.fileConfig`
function can be similar to: ::

    [handler_dbglog]
    class=spadl.DbgLogHandler
    level=NOTSET
    args=({'app': 4,
           'app.request': 3,
           'rpc': 2,
           '': 1},)

See (and run) `example.py` for the working example.
