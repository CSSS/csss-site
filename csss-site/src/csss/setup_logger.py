import datetime
import logging
import os
import shutil
import sys

import pytz
from django.conf import settings

from csss.CSSSLoggerHandlers import barrier_logging_level, CSSSDebugStreamHandler, CSSSErrorHandler

date_timezone = pytz.timezone('US/Pacific')


class PSTFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None, tz=None):
        super(PSTFormatter, self).__init__(fmt, datefmt)
        self.tz = tz

    def formatTime(self, record, datefmt=None):  # noqa: N802
        dt = datetime.datetime.fromtimestamp(record.created, self.tz)
        if datefmt:
            return dt.strftime(datefmt)
        else:
            return str(dt)


REDIRECT_STD_STREAMS = True
date_formatting_in_log = '%Y-%m-%d %H:%M:%S'
date_formatting_in_filename = "%Y_%m_%d_%H_%M_%S"
modular_log_prefix = "cmd_"
sys_stream_formatting = PSTFormatter(
    '%(asctime)s = %(levelname)s = %(name)s = %(message)s', date_formatting_in_log, tz=date_timezone
)


class Loggers:
    loggers = []
    logger_list_indices = {}
    django_settings_file_path_and_name = None
    sys_stream_error_log_file_absolute_path = None

    @classmethod
    def get_logger(cls, logger_name=None):
        if logger_name is None:
            if len(cls.loggers) == 0:
                raise Exception("Could not find any loggers")
            # handler_files = [
            #     handler.baseFilename for handler in cls.loggers[0].handlers if type(handler) is logging.FileHandler
            # ]
            # print(f"handler_file-first={handler_files[0]}")
            # print(f"handler_file-second={handler_files[1]}")
            # print("test")
            return cls.loggers[0]
        elif logger_name == settings.DJANGO_SETTINGS_LOG_HANDLER_NAME:
            return cls._add_logger(cls._add_settings_filehandler())
        elif logger_name == settings.SYS_STREAM_LOG_HANDLER_NAME:
            return cls._add_logger(cls._setup_sys_stream_logger())
        else:
            logger_name = cls.logger_name_formatter(logger_name)
            if logger_name in cls.logger_list_indices:
                return cls.loggers[cls.logger_list_indices[logger_name]]
            else:
                return cls._add_logger(cls._setup_logger(logger_name))

    @classmethod
    def _add_settings_filehandler(cls):
        # this is mostly here just so that the settings in the setting.spy can persist to all the debug logs
        # without other fluff being added to them
        date = datetime.datetime.now(date_timezone).strftime(date_formatting_in_filename)
        django_settings_logger = logging.getLogger(settings.DJANGO_SETTINGS_LOG_HANDLER_NAME)

        if not os.path.exists(f"{settings.LOG_LOCATION}/{settings.DJANGO_SETTINGS_LOG_HANDLER_NAME}"):
            os.mkdir(f"{settings.LOG_LOCATION}/{settings.DJANGO_SETTINGS_LOG_HANDLER_NAME}")

        django_settings_logger.setLevel(logging.DEBUG)
        cls.django_settings_file_path_and_name = (
            f"{settings.LOG_LOCATION}/{settings.DJANGO_SETTINGS_LOG_HANDLER_NAME}/{date}.log"
        )

        django_settings_filehandler = logging.FileHandler(cls.django_settings_file_path_and_name)
        django_settings_filehandler.setLevel(logging.DEBUG)
        django_settings_filehandler.setFormatter(sys_stream_formatting)
        django_settings_logger.addHandler(django_settings_filehandler)

        django_settings_error_filehandler = logging.FileHandler(
            f"{settings.LOG_LOCATION}/{settings.DJANGO_SETTINGS_LOG_HANDLER_NAME}/{date}_error.log"
        )
        django_settings_error_filehandler.setLevel(barrier_logging_level)
        django_settings_error_filehandler.setFormatter(sys_stream_formatting)
        django_settings_logger.addHandler(django_settings_error_filehandler)

        if REDIRECT_STD_STREAMS:
            sys.stdout = sys.__stdout__
        django_settings_stdout_stream_handler = CSSSDebugStreamHandler(sys.stdout)
        django_settings_stdout_stream_handler.setFormatter(sys_stream_formatting)
        django_settings_stdout_stream_handler.setLevel(logging.DEBUG)
        django_settings_logger.addHandler(django_settings_stdout_stream_handler)
        if REDIRECT_STD_STREAMS:
            sys.stdout = LoggerWriter(django_settings_logger.info)

        if REDIRECT_STD_STREAMS:
            sys.stderr = sys.__stderr__
        django_settings_stderr_stream_handler = CSSSErrorHandler(sys.stderr)
        django_settings_stderr_stream_handler.setFormatter(sys_stream_formatting)
        django_settings_stderr_stream_handler.setLevel(barrier_logging_level)
        django_settings_logger.addHandler(django_settings_stderr_stream_handler)
        if REDIRECT_STD_STREAMS:
            sys.stderr = LoggerWriter(django_settings_logger.error)

        return django_settings_logger

    @classmethod
    def _setup_sys_stream_logger(cls):
        date = datetime.datetime.now(date_timezone).strftime(date_formatting_in_filename)
        if not os.path.exists(settings.LOG_LOCATION):
            exit(f"Unable to find '{settings.LOG_LOCATION}'")
        if not os.path.exists(f"{settings.LOG_LOCATION}/{settings.SYS_STREAM_LOG_HANDLER_NAME}"):
            os.mkdir(f"{settings.LOG_LOCATION}/{settings.SYS_STREAM_LOG_HANDLER_NAME}")
        if not os.path.exists(f"{settings.LOG_LOCATION}/{settings.DJANGO_SETTINGS_LOG_HANDLER_NAME}"):
            os.mkdir(f"{settings.LOG_LOCATION}/{settings.DJANGO_SETTINGS_LOG_HANDLER_NAME}")

        sys_logger = logging.getLogger(settings.SYS_STREAM_LOG_HANDLER_NAME)
        sys_logger.setLevel(logging.DEBUG)

        debug_log_file_absolute_path = (
            f"{settings.LOG_LOCATION}/{settings.SYS_STREAM_LOG_HANDLER_NAME}/{date}_debug.log"
        )
        cls.sys_stream_error_log_file_absolute_path = (
            f"{settings.LOG_LOCATION}/{settings.SYS_STREAM_LOG_HANDLER_NAME}/{date}_error.log"
        )

        if REDIRECT_STD_STREAMS:
            shutil.copy(cls.django_settings_file_path_and_name, f"{debug_log_file_absolute_path}")

        # ensures that anything printed to this logger at level DEBUG or above goes to the specified file
        debug_filehandler = logging.FileHandler(debug_log_file_absolute_path)
        debug_filehandler.setLevel(logging.DEBUG)
        debug_filehandler.setFormatter(sys_stream_formatting)
        sys_logger.addHandler(debug_filehandler)

        # ensures that anything printed to this logger at level ERROR or above goes to the specified file
        error_filehandler = logging.FileHandler(cls.sys_stream_error_log_file_absolute_path)
        error_filehandler.setLevel(barrier_logging_level)
        error_filehandler.setFormatter(sys_stream_formatting)
        sys_logger.addHandler(error_filehandler)

        # ensures that anything from the log goes to the stdout
        if REDIRECT_STD_STREAMS:
            sys.stdout = sys.__stdout__
        sys_stdout_stream_handler = CSSSDebugStreamHandler(sys.stdout)
        sys_stdout_stream_handler.setFormatter(sys_stream_formatting)
        sys_stdout_stream_handler.setLevel(logging.DEBUG)
        sys_logger.addHandler(sys_stdout_stream_handler)
        if REDIRECT_STD_STREAMS:
            sys.stdout = LoggerWriter(sys_logger.info)

        if REDIRECT_STD_STREAMS:
            sys.stderr = sys.__stderr__
        sys_stderr_stream_handler = CSSSErrorHandler(
            sys.stderr, file_name=cls.sys_stream_error_log_file_absolute_path
        )
        sys_stderr_stream_handler.setFormatter(sys_stream_formatting)
        sys_stderr_stream_handler.setLevel(barrier_logging_level)
        sys_logger.addHandler(sys_stderr_stream_handler)
        if REDIRECT_STD_STREAMS:
            sys.stderr = LoggerWriter(sys_logger.error)

        return sys_logger

    @classmethod
    def _setup_logger(cls, logger_name):
        if len(cls.loggers) == 0:
            raise Exception("There is no base logger")

        date = datetime.datetime.now(date_timezone).strftime(date_formatting_in_filename)
        if not os.path.exists(settings.LOG_LOCATION):
            exit(f"Unable to find '{settings.LOG_LOCATION}'")
        if not os.path.exists(f"{settings.LOG_LOCATION}/{logger_name}"):
            os.mkdir(f"{settings.LOG_LOCATION}/{logger_name}")
        debug_log_file_absolute_path = f"{settings.LOG_LOCATION}/{logger_name}/{date}_debug.log"
        error_log_file_absolute_path = f"{settings.LOG_LOCATION}/{logger_name}/{date}_error.log"

        if REDIRECT_STD_STREAMS:
            shutil.copy(cls.django_settings_file_path_and_name, f"{debug_log_file_absolute_path}")

        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)

        debug_filehandler = logging.FileHandler(debug_log_file_absolute_path)
        debug_filehandler.setLevel(logging.DEBUG)
        debug_filehandler.setFormatter(sys_stream_formatting)
        logger.addHandler(debug_filehandler)

        error_filehandler = logging.FileHandler(error_log_file_absolute_path)
        error_filehandler.setFormatter(sys_stream_formatting)
        error_filehandler.setLevel(barrier_logging_level)
        logger.addHandler(error_filehandler)

        if REDIRECT_STD_STREAMS:
            sys.stdout = sys.__stdout__
        sys_stdout_stream_handler = CSSSDebugStreamHandler(sys.stdout)
        sys_stdout_stream_handler.setFormatter(sys_stream_formatting)
        sys_stdout_stream_handler.setLevel(logging.DEBUG)
        logger.addHandler(sys_stdout_stream_handler)
        if REDIRECT_STD_STREAMS:
            sys.stdout = LoggerWriter(logger.info)

        if REDIRECT_STD_STREAMS:
            sys.stderr = sys.__stderr__
        sys_sterr_stream_handler = CSSSErrorHandler(sys.stderr, file_name=error_log_file_absolute_path)
        sys_sterr_stream_handler.setFormatter(sys_stream_formatting)
        sys_sterr_stream_handler.setLevel(barrier_logging_level)
        logger.addHandler(sys_sterr_stream_handler)
        if REDIRECT_STD_STREAMS:
            sys.stderr = LoggerWriter(logger.error)

        return logger

    @classmethod
    def _add_logger(cls, logger):
        cls.loggers.insert(0, logger)
        cls.logger_list_indices = {}
        for (index, saved_logger) in enumerate(cls.loggers):
            cls.logger_list_indices[saved_logger.name] = index
        return logger

    @classmethod
    def remove_logger(cls, logger_name, format_logger_name=True):
        if format_logger_name:
            logger_name = cls.logger_name_formatter(logger_name)
        logger = cls.loggers[cls.logger_list_indices[logger_name]]
        [
            os.remove(handler.baseFilename) for handler in logger.handlers
            if (type(handler) == logging.FileHandler) and os.path.exists(handler.baseFilename)
            and (round(os.stat(handler.baseFilename).st_size) == 0)
        ]
        cls.loggers = [logger for logger in cls.loggers if logger.name != logger_name]
        cls.logger_list_indices = {}
        for (index, saved_logger) in enumerate(cls.loggers):
            cls.logger_list_indices[saved_logger.name] = index

    @classmethod
    def logger_name_formatter(cls, logger_name):
        return f"{modular_log_prefix}{logger_name}"

    @classmethod
    def setup_sys_stream_logger(cls):
        cls.remove_logger(settings.DJANGO_SETTINGS_LOG_HANDLER_NAME, format_logger_name=False)
        cls._add_logger(cls._setup_sys_stream_logger())


class LoggerWriter:
    def __init__(self, level):
        self.level = level

    def write(self, message):
        if message != '\n':
            self.level(message)

    def flush(self):
        pass
