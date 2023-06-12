from unittest import skip

from django.test import SimpleTestCase

from csss.W3CValidation import W3CValidation


class WorkshopsW3CValidationTest(SimpleTestCase):

    @skip("not ready for w3c validation")
    def test_workshops_page(self):
        W3CValidation().validate_page(path="/events/workshops")