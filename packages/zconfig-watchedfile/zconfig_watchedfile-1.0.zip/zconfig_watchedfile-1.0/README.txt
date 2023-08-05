===================
zconfig_watchedfile
===================

Provides a ZConfig statement to register a logging handler that uses a
`WatchedFileHandler`_, which is helpful for integrating with an external
logrotate service::

    %import zconfig_watchedfile
    <logger>
      name example

      <watchedfile>
        path /path/to/logfile.log
      </watchedfile>
    </logger>

The ``<watchedfile>`` supports both the default ZConfig settings for handlers
(formatter, dateformat, level) and the parameters of `WatchedFileHandler`_
(mode, encoding, delay).

This package is compatible with Python version 2.6 and 2.7.

.. _`WatchedFileHandler`: http://docs.python.org/2/library/logging.handlers.html#watchedfilehandler
