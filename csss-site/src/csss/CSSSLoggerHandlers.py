import logging

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
        from csss.setup_logger import Loggers
        request = None
        endpoint = None
        if record.name == "django.request":
            filename = Loggers.sys_stream_error_log_file_absolute_path
            message = " ".join([f"{exc_info}" for exc_info in record.exc_info])
            request = str(record.request.__dict__)
            endpoint = record.request.path
            record_type = 'django_request_record'
        else:
            # django-commands come here
            filename = self.file_name
            message = record.exc_test if record.exc_text is not None else record.message
            record_type = 'other_record'
        if len(CSSSError.objects.all().filter(message=message)) == 0:
            CSSSError(filename=filename, message=message, request=request, endpoint=endpoint, type=record_type).save()
        super().emit(record)
