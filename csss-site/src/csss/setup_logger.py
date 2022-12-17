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
formatting = logging.Formatter('%(asctime)s = %(levelname)s = %(name)s = %(message)s', date_formatting_in_log)
date_timezone = pytz.timezone('US/Pacific')
modular_log_prefix = "cmd_"

def get_logger():
    return Loggers.get_logger()


class Loggers:
    loggers = []
    logger_list_indices = {}
    debug_file_path_and_name = None

    @classmethod
    def get_logger(cls, logger_name=None, use_cron_logger=False):
        if logger_name is None:
            if len(cls.loggers) == 0:
                raise Exception("Could not find a logger")
            return cls.loggers[0]
        else:
            if use_cron_logger:
                cron_logger_name = f"{modular_log_prefix}cron_service"
                if cron_logger_name in cls.logger_list_indices:
                    return cls.loggers[cls.logger_list_indices[cron_logger_name]]
                raise Exception("Could not find cron logger")
            if logger_name != settings.SYS_STREAM_LOG_HANDLER_NAME:
                logger_name = f"{modular_log_prefix}{logger_name}"
                if logger_name in cls.logger_list_indices:
                    return cls.loggers[cls.logger_list_indices[logger_name]]
            return cls._add_logger(cls._setup_logger(logger_name=logger_name))

    @classmethod
    def _setup_logger(cls, logger_name=None):
        if logger_name == settings.SYS_STREAM_LOG_HANDLER_NAME:
            return cls._setup_sys_stream_logger()
        if len(cls.loggers) == 0:
            raise Exception("There is no base logger")
        if logger_name is None:
            raise Exception("Did not get a logger_name")

        date = datetime.datetime.now(date_timezone).strftime(date_formatting_in_filename)
        if not os.path.exists(settings.LOG_LOCATION):
            exit(f"Unable to find '{settings.LOG_LOCATION}'")
        if not os.path.exists(f"{settings.LOG_LOCATION}/{logger_name}"):
            os.mkdir(f"{settings.LOG_LOCATION}/{logger_name}")
        debug_log_file_absolute_path = f"{settings.LOG_LOCATION}/{logger_name}/{date}_debug.log"
        error_log_file_absolute_path = f"{settings.LOG_LOCATION}/{logger_name}/{date}_err.log"

        try:
            shutil.copy(cls.debug_file_path_and_name, f"{debug_log_file_absolute_path}")
        except Exception as e:
            print(e)

        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)

        debug_filehandler = logging.FileHandler(debug_log_file_absolute_path)
        debug_filehandler.setLevel(logging.DEBUG)
        debug_filehandler.setFormatter(formatting)
        logger.addHandler(debug_filehandler)

        error_filehandler = logging.FileHandler(error_log_file_absolute_path)
        error_filehandler.setFormatter(formatting)
        error_filehandler.setLevel(logging.ERROR)
        logger.addHandler(error_filehandler)

        sys_stdout_stream_handler = logging.StreamHandler(sys.stdout)
        sys_stdout_stream_handler.setFormatter(formatting)
        sys_stdout_stream_handler.setLevel(logging.DEBUG)
        logger.addHandler(sys_stdout_stream_handler)

        # add method for going through the logs in realtime and emailing to csss-syadmin if there is an error or exception
        # use logging.exception("message")
        # also remove logs from more than a month ago

        return logger

    @classmethod
    def _setup_sys_stream_logger(cls):
        date = datetime.datetime.now(date_timezone).strftime(date_formatting_in_filename)
        if not os.path.exists(settings.LOG_LOCATION):
            exit(f"Unable to find '{settings.LOG_LOCATION}'")
        if not os.path.exists(f"{settings.LOG_LOCATION}/{settings.SYS_STREAM_LOG_HANDLER_NAME}"):
            os.mkdir(f"{settings.LOG_LOCATION}/{settings.SYS_STREAM_LOG_HANDLER_NAME}")

        sys_logger = logging.getLogger(settings.SYS_STREAM_LOG_HANDLER_NAME)
        sys_logger.setLevel(logging.DEBUG)

        # ensures that anything printed to this logger at level DEBUG or above goes to the specified file
        cls.debug_file_path_and_name = f"{settings.LOG_LOCATION}/{settings.SYS_STREAM_LOG_HANDLER_NAME}/{date}_debug.log"
        debug_filehandler = logging.FileHandler(cls.debug_file_path_and_name)
        debug_filehandler.setLevel(logging.DEBUG)
        debug_filehandler.setFormatter(formatting)
        sys_logger.addHandler(debug_filehandler)

        # ensures that anything printed to this logger at level ERROR or above goes to the specified file
        error_filehandler = logging.FileHandler(f"{settings.LOG_LOCATION}/{settings.SYS_STREAM_LOG_HANDLER_NAME}/{date}_err.log")
        error_filehandler.setLevel(logging.ERROR)
        error_filehandler.setFormatter(formatting)
        sys_logger.addHandler(error_filehandler)

        # ensures that anything from the log goes to the stdout
        sys_stdout_stream_handler = logging.StreamHandler(sys.stdout)
        sys_stdout_stream_handler.setFormatter(formatting)
        sys_stdout_stream_handler.setLevel(logging.DEBUG)
        sys_logger.addHandler(sys_stdout_stream_handler)

        # ensures that anything that goes to stdout also goes to the logger which is directed back to the console
        # thanks to the sys_stdout_stream_handler
        sys.stdout = LoggerWriter(sys_logger.info)

        # ensures that anything that goes to stderr also goes to the logger which is directed back to the console
        # thanks to the sys_stdout_stream_handler
        sys.stderr = LoggerWriter(sys_logger.error)
        return sys_logger

    @classmethod
    def _add_logger(cls, logger):
        cls.loggers.insert(0, logger)
        for (index, saved_logger) in enumerate(cls.loggers):
            cls.logger_list_indices[saved_logger.name] = index
        return logger

    @classmethod
    def remove_logger(cls, logger_name):
        cls.loggers = [logger for logger in cls.loggers if logger.name != logger_name]
        for (index, saved_logger) in enumerate(cls.loggers):
            cls.logger_list_indices[saved_logger.name] = index


class LoggerWriter:
    def __init__(self, level):
        self.level = level
        self.pattern_for_message_with_formatting = re.compile(
            "^\d{4}-\d{1,2}-\d{1,2} \d{1,2}:\d{1,2}:\d{1,2} = (" +
            ("|".join(list(logging._nameToLevel.keys()))) +
            ") = \w+ = "
        )

    def write(self, message):
        if message != '\n':
            """
            this bit a hack logic it just a way to transform a line of log from
            2022-12-16 19:24:36 = INFO = std_stream = 2022-12-16 19:24:36 = INFO = command_logs_cron_service = [csss/cron_service.py cron()] job nag_officers_to_enter_info added to the scheduler
            to
            2022-12-16 19:24:36 = INFO = std_stream = command_logs_cron_service = [csss/cron_service.py cron()] job nag_officers_to_enter_info added to the scheduler
            not perfect but best way I could think of to reduce the redundacies and line length while also not creating confusion as to which logger the line originated from
            """
            pattern_match = self.pattern_for_message_with_formatting.match(message)
            if pattern_match is not None:
                pattern_match_lower_bound = pattern_match.regs[0][0]
                pattern_match_upper_bound = pattern_match.regs[0][1]
                level = message[pattern_match_lower_bound:pattern_match_upper_bound].split(" = ")[1]
                logger_name = message[pattern_match_lower_bound:pattern_match_upper_bound].split(" = ")[2]
                message = f"{level} = {logger_name} = {message[pattern_match_upper_bound:]}"
            # lines from `logger.level` seem to get a newline added on that is then duplicated with the call to self.level
            # so remove that newline before another one gets added on
            if len(message) > 0 and message[-1:] == "\n":
                message = message[:-1]
            self.level(message)

    def flush(self):
        pass
