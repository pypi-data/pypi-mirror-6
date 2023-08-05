__import__("pkg_resources").declare_namespace(__name__)

import os
import sys
import logging
import StringIO
import time

FORMATTER_KWARGS = dict(fmt='%(asctime)-25s %(levelname)-8s %(name)-50s %(message)s', datefmt='%Y-%m-%d %H:%M:%S %z')

def can_user_write_in_directory(dirpath):
    from os import path, remove, getpid
    src = path.join(dirpath, 'test-permissions.{}'.format(getpid()))
    try:
        with open(src, 'w'):
            pass
        remove(src)
    except IOError:
        return False
    return True


class LogFileHandler(logging.FileHandler): # pragma: no cover
    def __init__(self, program_name, mode='a', encoding=None, delay=0):
        self._program_name = program_name
        filename = self.get_logfile_path()
        logging.FileHandler.__init__(self, filename, mode=mode, encoding=encoding, delay=delay)
        self._filename = filename

    def _get_logfile_filename(self):
        path = ".".join([self._program_name, self.get_timestamp(), "debug", "log"])
        index = 1
        while os.path.exists(os.path.join(self.get_logs_directory(), path)):
            path = ".".join([self._program_name, "{}-{}".format(self.get_timestamp(), index), "debug", "log"])
            index += 1
        return path

    def get_logfile_path(self):
        self._path = getattr(self, "_path",
                       os.path.join(self.get_logs_directory(), self._get_logfile_filename()))
        return self._path

    @classmethod
    def get_logs_directory(cls):
        if os.name == "nt":
            return os.environ.get("Temp", os.path.join(os.environ.get("SystemRoot", r"C:\Windows"), "Temp"))
        else:
            tmp = os.path.join(os.path.sep, 'tmp')
            var_log = os.path.join(os.path.sep, 'var', 'log')
            if can_user_write_in_directory(var_log):
                return var_log
            return tmp

    @classmethod
    def get_timestamp(self):
        return time.strftime("%Y-%m-%d.%H-%M")


class DiskBackedStringIO(StringIO.StringIO):
    def __init__(self, filename, stream):
        StringIO.StringIO.__init__(self)
        self._fd = open(filename, 'a')
        self._stream = stream

    def write(self, *args, **kwargs):
        self._fd.write(*args, **kwargs)
        self._stream.write(*args, **kwargs)


class BuildoutLogging(object):
    is_set = False
    def __init__(self, buildout, name, options):
        super(BuildoutLogging, self).__init__()
        self.buildout = buildout
        self.name = name
        self.options = options

    def _setup(self):
        if BuildoutLogging.is_set:
            return []
        handler = self._get_logging_handler()
        sys.stdout = DiskBackedStringIO(handler._filename.replace("debug", "stdout"), sys.stdout)
        sys.stderr = DiskBackedStringIO(handler._filename.replace("debug", "stderr"), sys.stderr)
        self._setup_logging(handler)
        BuildoutLogging.is_set = True
        return  []

    def update(self):
        return self._setup()

    def install(self):
        return self._setup()

    def _get_logging_handler(self):
        handler = LogFileHandler("buildout")
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(logging.Formatter(**FORMATTER_KWARGS))
        return handler

    def _setup_logger(self, logger, handler):
        self._handler = handler
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)

    def _setup_logging(self, handler):
        self._setup_logger(logging.root, handler)
        for logger in [item for item in set(logging.Logger.manager.loggerDict.values())
                       if isinstance(item, logging.Logger) and item.handlers]:
            logger.handlers[0].stream = sys.stdout
            self._setup_logger(logger, handler)
