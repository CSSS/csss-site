from unittest import skip

from django.test import SimpleTestCase

from csss.W3CValidation import W3CValidation


class CSSSW3CValidationTest(SimpleTestCase):

    @skip("not ready for w3c validation")
    def test_home_page(self):
        W3CValidation().validate_page(path="/")

    def test_markdown_page(self):
        W3CValidation().validate_page(path="/markdown")

    @skip("not ready for w3c validation")
    def test_cron_jobs_page(self):
        W3CValidation().validate_page(path="/cron")

    @skip("not ready for w3c validation")
    def test_cron_logs_page(self):
        W3CValidation().validate_page(path="/cron_logs")
