import datetime
import logging
import os
import shutil

import pytz
import sys

from django.conf import settings


class SettingsLogger(object):
    def __init__(self, std_terminal, filename):
        self.terminal = std_terminal
        self.log = open(filename, "w")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        pass


def get_logger(cron_module=None, use_existing_logging=True):
    if use_existing_logging:
        loggers = [
            logging.getLogger(logger) for logger in logging.root.manager.loggerDict
            if "command_logs_" in logger or "csss_site_settings" == logger
        ]
        if len(loggers) > 1:
            raise Exception("There seems to be more than 1 logger setup..")
        if len(loggers) == 1:
            return loggers[0]

    if cron_module is not None:
        logger_name = f"command_logs_{cron_module}"
    else:
        logger_name = "csss_site_settings"
    loggers = [
        logging.getLogger(logger) for logger in logging.root.manager.loggerDict
        if logger_name == logger
    ]
    if len(loggers) > 1:
        raise Exception("There seems to be more than 1 logger setup..")

    return loggers[0] if len(loggers) == 1 else _setup_logger(cron_module=cron_module)


def _setup_logger(cron_module=None):
    if cron_module is None:
        cron_module = "csss_site_settings"
    else:
        cron_module = f"command_logs_{cron_module}"

    date = datetime.datetime.now(pytz.timezone('US/Pacific')).strftime("%Y_%m_%d_%H_%M_%S")
    if not os.path.exists(settings.LOG_LOCATION):
        exit(f"Unable to find '{settings.LOG_LOCATION}'")
    if not os.path.exists(f"{settings.LOG_LOCATION}/{cron_module}"):
        os.mkdir(f"{settings.LOG_LOCATION}/{cron_module}")
    debug_log_file_absolute_path = f"{settings.LOG_LOCATION}/{cron_module}/{date}_csss_site.log"
    error_log_file_absolute_path = f"{settings.LOG_LOCATION}/{cron_module}/{date}_csss_site_errors.log"

    if os.path.exists(settings.SETTINGS_ERROR_LOG_LOCATION):
        # this is here just so the prints in settings.py also go to the individual log files
        try:
            shutil.move(settings.SETTINGS_ERROR_LOG_LOCATION, f"{error_log_file_absolute_path}")
        except Exception as e:
            print(e)

    if os.path.exists(settings.SETTINGS_LOG_LOCATION):
        # this is here just so the prints in settings.py also go to the individual log files
        try:
            shutil.move(settings.SETTINGS_LOG_LOCATION, f"{debug_log_file_absolute_path}")
        except Exception as e:
            print(e)

    logger = logging.getLogger(cron_module)
    logger.setLevel(logging.DEBUG)

    formatting = logging.Formatter('%(asctime)s = %(levelname)s - %(message)s', '%Y-%m-%d %H:%M:%S')

    debug_filehandler = logging.FileHandler(debug_log_file_absolute_path)
    debug_filehandler.setLevel(logging.DEBUG)
    debug_filehandler.setFormatter(formatting)
    logger.addHandler(debug_filehandler)

    error_filehandler = logging.FileHandler(error_log_file_absolute_path)
    error_filehandler.setFormatter(formatting)
    error_filehandler.setLevel(logging.ERROR)
    logger.addHandler(error_filehandler)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatting)
    stream_handler.setLevel(logging.DEBUG)
    logger.addHandler(stream_handler)

    # add method for going through the logs in realtime and emailing to csss-syadmin if there is an error or exception
    # use logging.exception("message")
    # also remove logs from more than a month ago

    sys.stdout = LoggerWriter(logger.info)
    sys.stderr = LoggerWriter(logger.error)
    return logger


class LoggerWriter:
    def __init__(self, level):
        self.level = level

    def write(self, message):
        if message != '\n':
            self.level(message)

    def flush(self):
        pass
