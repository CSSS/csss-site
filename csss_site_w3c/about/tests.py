from unittest import skip

from django.test import SimpleTestCase

from csss.W3CValidation import W3CValidation


class AboutW3CValidationTest(SimpleTestCase):

    @skip("not ready for w3c validation")
    def test_list_of_current_officers(self):
        W3CValidation().validate_page(path="/about/list_of_current_officers")

    @skip("not ready for w3c validation")
    def test_list_of_past_officers(self):
        W3CValidation().validate_page(path="/about/list_of_past_officers")

    def test_who_we_are(self):
        W3CValidation().validate_page(path="/about/who_we_are")
