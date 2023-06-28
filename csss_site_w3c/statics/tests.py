from django.test import SimpleTestCase

from csss.W3CValidation import W3CValidation


class StaticsW3CValidationTest(SimpleTestCase):

    def test_bursaries_page(self):
        W3CValidation().validate_page(path="/statics/bursaries")

    def test_guide_page(self):
        W3CValidation().validate_page(path="/statics/guide")

    def test_getting_started_page(self):
        W3CValidation().validate_page(path="/statics/getting_started")
