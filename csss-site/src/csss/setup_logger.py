import datetime
import logging
import os
import re
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


def get_logger():
    return Loggers.get_logger()


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
    def _setup_logger(cls, logger_name):
        if len(cls.loggers) == 0:
            raise Exception("There is no base logger")

        date = datetime.datetime.now(date_timezone).strftime(date_formatting_in_filename)
        if not os.path.exists(settings.LOG_LOCATION):
            exit(f"Unable to find '{settings.LOG_LOCATION}'")
        if not os.path.exists(f"{settings.LOG_LOCATION}/{logger_name}"):
            os.mkdir(f"{settings.LOG_LOCATION}/{logger_name}")
        debug_log_file_absolute_path = f"{settings.LOG_LOCATION}/{logger_name}/{date}_debug.log"
        error_log_file_absolute_path = f"{settings.LOG_LOCATION}/{logger_name}/{date}_err.log"

        shutil.copy(cls.django_settings_file_path_and_name, f"{debug_log_file_absolute_path}")

        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)

        debug_filehandler = logging.FileHandler(debug_log_file_absolute_path)
        debug_filehandler.setLevel(logging.DEBUG)
        debug_filehandler.setFormatter(sys_stream_formatting)
        logger.addHandler(debug_filehandler)

        error_filehandler = logging.FileHandler(error_log_file_absolute_path)
        error_filehandler.setFormatter(sys_stream_formatting)
        error_filehandler.setLevel(logging.ERROR)
        logger.addHandler(error_filehandler)

        sys_stdout_stream_handler = logging.StreamHandler(sys.stdout)

        sys_stdout_stream_handler.setFormatter(sys_stream_formatting)
        sys_stdout_stream_handler.setLevel(logging.DEBUG)
        logger.addHandler(sys_stdout_stream_handler)

        # ensures that anything that goes to stderr also goes to the logger which is directed back to the console
        # thanks to the sys_stdout_stream_handler
        sys.stderr = LoggerWriter(logger.error, "ERROR")

        # ensures that anything that goes to stdout also goes to the logger which is directed back to the console
        # thanks to the sys_stdout_stream_handler
        sys.stdout = LoggerWriter(logger.info, "INFO")
        # add method for going through the logs in realtime and emailing to csss-syadmin if there is an error or
        # exception
        # use logging.exception("message") also remove logs from more than a month ago

        return logger

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

        # ensures that anything printed to this logger at level DEBUG or above goes to the specified file
        debug_filehandler = logging.FileHandler(
            f"{settings.LOG_LOCATION}/{settings.SYS_STREAM_LOG_HANDLER_NAME}/{date}_debug.log")
        debug_filehandler.setLevel(logging.DEBUG)
        debug_filehandler.setFormatter(sys_stream_formatting)
        sys_logger.addHandler(debug_filehandler)

        # ensures that anything printed to this logger at level ERROR or above goes to the specified file
        error_filehandler = logging.FileHandler(
            f"{settings.LOG_LOCATION}/{settings.SYS_STREAM_LOG_HANDLER_NAME}/{date}_err.log")
        error_filehandler.setLevel(logging.ERROR)
        error_filehandler.setFormatter(sys_stream_formatting)
        sys_logger.addHandler(error_filehandler)

        # ensures that anything from the log goes to the stdout
        sys_stdout_stream_handler = logging.StreamHandler(sys.stdout)
        sys_stdout_stream_handler.setFormatter(sys_stream_formatting)
        sys_stdout_stream_handler.setLevel(logging.DEBUG)
        sys_logger.addHandler(sys_stdout_stream_handler)

        # ensures that anything that goes to stderr also goes to the logger which is directed back to the console
        # thanks to the sys_stdout_stream_handler
        sys.stderr = LoggerWriter(sys_logger.error, "ERROR")

        # ensures that anything that goes to stdout also goes to the logger which is directed back to the console
        # thanks to the sys_stdout_stream_handler
        sys.stdout = LoggerWriter(sys_logger.info, "INFO")

        return sys_logger

    @classmethod
    def _add_settings_filehandler(cls):
        date = datetime.datetime.now(date_timezone).strftime(date_formatting_in_filename)

        # this is mostly here just so that the settings in the setting.spy can persist to all the debug logs
        # without other fluff being added to them
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

        django_settings_error_filehandler = logging.FileHandler(f"{settings.LOG_LOCATION}/{settings.DJANGO_SETTINGS_LOG_HANDLER_NAME}/{date}_error.log")
        django_settings_error_filehandler.setLevel(logging.ERROR)
        django_settings_error_filehandler.setFormatter(sys_stream_formatting)
        django_settings_logger.addHandler(django_settings_error_filehandler)

        django_settings_stream_handler = logging.StreamHandler(sys.stdout)
        django_settings_stream_handler.setFormatter(sys_stream_formatting)
        django_settings_stream_handler.setLevel(logging.DEBUG)
        django_settings_logger.addHandler(django_settings_stream_handler)


        # ensures that anything that goes to stderr also goes to the logger which is directed back to the console
        # thanks to the sys_stdout_stream_handler
        sys.stderr = LoggerWriter(django_settings_logger.error, "ERROR")

        # ensures that anything that goes to stdout also goes to the logger which is directed back to the console
        # thanks to the sys_stdout_stream_handler
        sys.stdout = LoggerWriter(django_settings_logger.info, "INFO")

        return django_settings_logger

    @classmethod
    def _add_logger(cls, logger):
        cls.loggers.insert(0, logger)
        for (index, saved_logger) in enumerate(cls.loggers):
            cls.logger_list_indices[saved_logger.name] = index
        return logger

    @classmethod
    def remove_logger(cls, logger_name, format_logger_name=True):
        if format_logger_name:
            logger_name = cls.logger_name_formatter(logger_name)
        cls.loggers = [logger for logger in cls.loggers if logger.name != logger_name]
        cls.logger_list_indices = {}
        for (index, saved_logger) in enumerate(cls.loggers):
            cls.logger_list_indices[saved_logger.name] = index

    @classmethod
    def logger_name_formatter(cls, logger_name):
        return f"{modular_log_prefix}{logger_name}"

    @classmethod
    def setup_sys_stream_logger(cls):
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        cls.remove_logger(settings.DJANGO_SETTINGS_LOG_HANDLER_NAME, format_logger_name=False)
        cls._add_logger(cls._setup_sys_stream_logger())


class LoggerWriter:
    def __init__(self, level, level_name):
        self.level = level
        self.level_name = level_name
        self.pattern_for_message_with_formatting = re.compile(
            r"^\d{4}-\d{1,2}-\d{1,2} \d{1,2}:\d{1,2}:\d{1,2} = (" +
            ("|".join(list(logging._nameToLevel.keys()))) +
            r") = \w+ = "
        )

    def write(self, message):
        if message != '\n':
            self.level(message)

    def flush(self):
        pass
