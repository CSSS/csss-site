from unittest import skip

from django.test import SimpleTestCase

from csss.W3CValidation import W3CValidation


class MountainMadnessW3CValidationTest(SimpleTestCase):

    def test_mm_2023_page(self):
        W3CValidation().validate_page(path="/events/mm/2023")


    @skip("not ready for w3c validation")
    def test_mm_2022_page(self):
        W3CValidation().validate_page(path="/events/mm/2022")

    def test_mm_2021_submissions_page(self):
        W3CValidation().validate_page(path="/events/mm/2021/submissions")

    @skip("not ready for w3c validation")
    def test_mm_2021_page(self):
        W3CValidation().validate_page(path="/events/mm/2021")

    @skip("not ready for w3c validation")
    def test_mm_2020_page(self):
        W3CValidation().validate_page(path="/events/mm/2020")

    @skip("not ready for w3c validation")
    def test_mm_2019_page(self):
        W3CValidation().validate_page(path="/events/mm/2019")