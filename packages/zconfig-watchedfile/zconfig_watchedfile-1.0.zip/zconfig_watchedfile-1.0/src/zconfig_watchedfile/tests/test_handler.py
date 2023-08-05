from StringIO import StringIO
import ZConfig
import logging
import logging.handlers
import pkg_resources
import pytest


@pytest.fixture(autouse=True)
def logger(request):
    def reset_handler():
        logging.getLogger('foo').handlers[:] = []
    request.addfinalizer(reset_handler)


def load_config(config):
    schema = ZConfig.loadSchemaFile(open(pkg_resources.resource_filename(
        __name__, 'schema.xml')))
    conf, handler = ZConfig.loadConfigFile(schema, StringIO(config))
    return conf.loggers


def test_creates_watchedfilehandler():
    loggers = load_config("""
%import zconfig_watchedfile
<logger>
   name foo

   <watchedfile>
     path /dev/null
   </watchedfile>
</logger>
""")
    logger = loggers[0].create()
    assert isinstance(logger.handlers[0], logging.handlers.WatchedFileHandler)
    assert '/dev/null' == logger.handlers[0].baseFilename


def test_passes_parameters():
    loggers = load_config("""
%import zconfig_watchedfile
<logger>
   name foo

   <watchedfile>
     path /dev/null
     mode w
     encoding utf-8
     delay true
   </watchedfile>
</logger>
""")
    logger = loggers[0].create()
    handler = logger.handlers[0]
    assert 'w' == handler.mode
    assert 'utf-8' == handler.encoding
    assert handler.delay
