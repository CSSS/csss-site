import datetime
import logging
import os
import shutil
import sys

import pytz
from django.conf import settings

date_formatting_in_log = '%Y-%m-%d %H:%M:%S'
date_formatting_in_filename = "%Y_%m_%d_%H_%M_%S"
sys_stream_formatting = logging.Formatter(
    '%(asctime)s = %(levelname)s = %(name)s = %(message)s', date_formatting_in_log
)

date_timezone = pytz.timezone('US/Pacific')
modular_log_prefix = "cmd_"

barrier_logging_level = logging.ERROR


class CSSSDebugStreamHandler(logging.StreamHandler):
    def emit(self, record):
        if record.levelno < barrier_logging_level:
            super().emit(record)


class CSSSErrorHandler(logging.StreamHandler):

    def __init__(self, stream=None, file_name=None):
        self.file_name = file_name
        super().__init__(stream)

    def emit(self, record):
        from csss.models import CSSSError
        if len(CSSSError.objects.all().exclude(message=record.message)) == 0:
            CSSSError(filename=self.file_name, message=record.message).save()
        super().emit(record)


class Loggers:
    loggers = []
    logger_list_indices = {}
    django_settings_file_path_and_name = None

    @classmethod
    def get_logger(cls, logger_name=None):
        if logger_name is None:
            if len(cls.loggers) == 0:
                raise Exception("Could not find any loggers")
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

        sys.stdout = sys.__stdout__
        django_settings_stdout_stream_handler = CSSSDebugStreamHandler(sys.stdout)
        django_settings_stdout_stream_handler.setFormatter(sys_stream_formatting)
        django_settings_stdout_stream_handler.setLevel(logging.DEBUG)
        django_settings_logger.addHandler(django_settings_stdout_stream_handler)
        sys.stdout = LoggerWriter(django_settings_logger.info)

        sys.stderr = sys.__stderr__
        django_settings_stderr_stream_handler = CSSSErrorHandler(sys.stderr)
        django_settings_stderr_stream_handler.setFormatter(sys_stream_formatting)
        django_settings_stderr_stream_handler.setLevel(barrier_logging_level)
        django_settings_logger.addHandler(django_settings_stderr_stream_handler)
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
        error_log_file_absolute_path = (
            f"{settings.LOG_LOCATION}/{settings.SYS_STREAM_LOG_HANDLER_NAME}/{date}_error.log"
        )

        shutil.copy(cls.django_settings_file_path_and_name, f"{debug_log_file_absolute_path}")

        # ensures that anything printed to this logger at level DEBUG or above goes to the specified file
        debug_filehandler = logging.FileHandler(debug_log_file_absolute_path)
        debug_filehandler.setLevel(logging.DEBUG)
        debug_filehandler.setFormatter(sys_stream_formatting)
        sys_logger.addHandler(debug_filehandler)

        # ensures that anything printed to this logger at level ERROR or above goes to the specified file
        error_filehandler = logging.FileHandler(error_log_file_absolute_path)
        error_filehandler.setLevel(barrier_logging_level)
        error_filehandler.setFormatter(sys_stream_formatting)
        sys_logger.addHandler(error_filehandler)

        # ensures that anything from the log goes to the stdout
        sys.stdout = sys.__stdout__
        sys_stdout_stream_handler = CSSSDebugStreamHandler(sys.stdout)
        sys_stdout_stream_handler.setFormatter(sys_stream_formatting)
        sys_stdout_stream_handler.setLevel(logging.DEBUG)
        sys_logger.addHandler(sys_stdout_stream_handler)
        sys.stdout = LoggerWriter(sys_logger.info)

        sys.stderr = sys.__stderr__
        sys_stderr_stream_handler = CSSSErrorHandler(sys.stderr, file_name=error_log_file_absolute_path)
        sys_stderr_stream_handler.setFormatter(sys_stream_formatting)
        sys_stderr_stream_handler.setLevel(barrier_logging_level)
        sys_logger.addHandler(sys_stderr_stream_handler)
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

        sys.stdout = sys.__stdout__
        sys_stdout_stream_handler = CSSSDebugStreamHandler(sys.stdout)
        sys_stdout_stream_handler.setFormatter(sys_stream_formatting)
        sys_stdout_stream_handler.setLevel(logging.DEBUG)
        logger.addHandler(sys_stdout_stream_handler)
        sys.stdout = LoggerWriter(logger.info)

        sys.stderr = sys.__stderr__
        sys_sterr_stream_handler = CSSSErrorHandler(sys.stderr, file_name=error_log_file_absolute_path)
        sys_sterr_stream_handler.setFormatter(sys_stream_formatting)
        sys_sterr_stream_handler.setLevel(barrier_logging_level)
        logger.addHandler(sys_sterr_stream_handler)
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
            if (type(handler) == logging.FileHandler) and (round(os.stat(handler.baseFilename).st_size) == 0)
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
