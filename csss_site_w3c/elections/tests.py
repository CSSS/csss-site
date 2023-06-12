from unittest import skip

from django.test import SimpleTestCase

from csss.W3CValidation import W3CValidation


class ElectionsW3CValidationTest(SimpleTestCase):

    def test_elections_page(self):
        W3CValidation().validate_page(path="/elections")

    @skip("not ready for w3c validation")
    def test_most_recent_election_page(self):
        W3CValidation().validate_page(path="/elections/2023-03-29-general_election")
