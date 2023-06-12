from django.test import SimpleTestCase

from csss.W3CValidation import W3CValidation


class EventsW3CValidationTest(SimpleTestCase):

    def test_regular_events_page(self):
        W3CValidation().validate_page(path="/events/regular_events")
