import datetime
import logging
import os
import re
import shutil
import sys

import pytz
from django.conf import settings

formatting = logging.Formatter('%(asctime)s = %(name)s = %(levelname)s - %(message)s', '%Y-%m-%d %H:%M:%S')


def get_logger():
    return Loggers.get_logger()


class Loggers:
    loggers = None

    @classmethod
    def get_logger(cls, get_latest_logs=False):
        if get_latest_logs or cls.loggers is None:
            cls.loggers = [
                logging.getLogger(logger) for logger in logging.root.manager.loggerDict
                if "command_logs_" in logger or "std_stream" == logger
            ]
        if len(cls.loggers) == 0:
            raise Exception("Could not find a logger")
        if len(cls.loggers) == 1:
            return cls.loggers[0]
        else:
            raise Exception("Found a logger both for a command and runserver")


def setup_std_stream_logger():
    stream_name = "std_stream"
    sys_stream_logger = logging.getLogger(stream_name)
    sys_stream_logger.setLevel(logging.DEBUG)

    date = datetime.datetime.now(pytz.timezone('US/Pacific')).strftime("%Y_%m_%d")
    if not os.path.exists(settings.LOG_LOCATION):
        exit(f"Unable to find '{settings.LOG_LOCATION}'")
    if not os.path.exists(f"{settings.LOG_LOCATION}/{stream_name}"):
        os.mkdir(f"{settings.LOG_LOCATION}/{stream_name}")

    # ensures that anything printed to this logger from level DEBUG or above goes to the sys.__stdout__
    sys_stdout_stream_handler = logging.StreamHandler(sys.stdout)
    sys_stdout_stream_handler.setFormatter(formatting)
    sys_stdout_stream_handler.setLevel(logging.DEBUG)
    sys_stream_logger.addHandler(sys_stdout_stream_handler)

    # ensures that anything printed to this logger at level DEBUR or above goes to the specified file
    debug_filehandler = logging.FileHandler(f"{settings.LOG_LOCATION}/{stream_name}/{date}_csss_site_debugs.log")
    debug_filehandler.setLevel(logging.DEBUG)
    debug_filehandler.setFormatter(formatting)
    sys_stream_logger.addHandler(debug_filehandler)

    # ensures that anything printed to sys.stdout goes to the INFO level of logger sys_stream_logger
    sys.stdout = LoggerWriter(sys_stream_logger.info)

    # ensures that anything printed to this logger from level ERROR or above goes to the sys.__stderr__
    sys_sterr_stream_handler = logging.StreamHandler(sys.stderr)
    sys_sterr_stream_handler.setFormatter(formatting)
    sys_sterr_stream_handler.setLevel(logging.ERROR)
    sys_stream_logger.addHandler(sys_sterr_stream_handler)

    # ensures that anything printed to this logger at level ERROR or above goes to the specified file
    error_filehandler = logging.FileHandler(f"{settings.LOG_LOCATION}/{stream_name}/{date}_csss_site_errors.log")
    error_filehandler.setFormatter(formatting)
    error_filehandler.setLevel(logging.ERROR)
    sys_stream_logger.addHandler(error_filehandler)

    # ensures that anything printed to sys.stderr goes to the ERROR level of logger sys_stream_logger
    sys.stderr = LoggerWriter(sys_stream_logger.error)


def setup_std_stream_logger_v2():
    stream_name = "std_stream"
    date = datetime.datetime.now(pytz.timezone('US/Pacific')).strftime("%Y_%m_%d_%H_%M_%S")
    if not os.path.exists(settings.LOG_LOCATION):
        exit(f"Unable to find '{settings.LOG_LOCATION}'")
    if not os.path.exists(f"{settings.LOG_LOCATION}/{stream_name}"):
        os.mkdir(f"{settings.LOG_LOCATION}/{stream_name}")

    sys_logger = logging.getLogger(stream_name)
    sys_logger.setLevel(logging.DEBUG)

    # ensures that anything printed to this logger at level DEBUG or above goes to the specified file
    debug_filehandler = logging.FileHandler(f"{settings.LOG_LOCATION}/{stream_name}/{date}_csss_site_debugs.log")
    debug_filehandler.setLevel(logging.DEBUG)
    debug_filehandler.setFormatter(formatting)
    sys_logger.addHandler(debug_filehandler)

    # ensures that anything printed to this logger at level ERROR or above goes to the specified file
    error_filehandler = logging.FileHandler(f"{settings.LOG_LOCATION}/{stream_name}/{date}_csss_site_errors.log")
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
    sys.stdout = LoggerWriter(sys_logger.debug)

    # ensures that anything that goes to stderr also goes to the logger which is directed back to the console
    # thanks to the sys_stdout_stream_handler
    sys.stderr = LoggerWriter(sys_logger.error)


def get_or_setup_logger(logger_name=None):
    if sys.stdout == sys.__stdout__:
        setup_std_stream_logger_v2()
    if logger_name is not None:
        logger_name = f"command_logs_{logger_name}"
    else:
        logger_name = "std_stream"
    loggers = [
        logging.getLogger(logger) for logger in logging.root.manager.loggerDict
        if logger_name == logger
    ]
    if len(loggers) > 1:
        raise Exception("There seems to be more than 1 logger setup..")
    if len(loggers) == 1:
        return loggers[0]

    date = datetime.datetime.now(pytz.timezone('US/Pacific')).strftime("%Y_%m_%d_%H_%M_%S")
    if not os.path.exists(settings.LOG_LOCATION):
        exit(f"Unable to find '{settings.LOG_LOCATION}'")
    if not os.path.exists(f"{settings.LOG_LOCATION}/{logger_name}"):
        os.mkdir(f"{settings.LOG_LOCATION}/{logger_name}")
    debug_log_file_absolute_path = f"{settings.LOG_LOCATION}/{logger_name}/{date}_csss_site_debugs.log"
    error_log_file_absolute_path = f"{settings.LOG_LOCATION}/{logger_name}/{date}_csss_site_errors.log"

    try:
        shutil.copy(settings.DEBUG_LOG_LOCATION, f"{debug_log_file_absolute_path}")
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


class LoggerWriter:
    def __init__(self, level):
        self.level = level

    def write(self, message):
        if message != '\n':
            self.level(message)

    def flush(self):
        pass
