import ZConfig.components.logger.handlers
import logging.handlers


class WatchedFileHandlerFactory(
        ZConfig.components.logger.handlers.HandlerFactory):

    def create_loghandler(self):
        return logging.handlers.WatchedFileHandler(
            self.section.path,
            mode=self.section.mode, encoding=self.section.encoding,
            delay=self.section.delay)
