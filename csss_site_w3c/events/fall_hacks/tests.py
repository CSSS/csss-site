from unittest import skip

from django.test import SimpleTestCase

from csss.W3CValidation import W3CValidation


class FallHacksW3CValidationTest(SimpleTestCase):

    @skip("not ready for w3c validation")
    def test_fall_hacks_2020(self):
        W3CValidation().validate_page(path="/events/regular_events/fall_hacks/2020")

    @skip("not ready for w3c validation")
    def test_fall_hacks_2020_submissions(self):
        W3CValidation().validate_page(path="/events/regular_events/fall_hacks/2020/submissions")
