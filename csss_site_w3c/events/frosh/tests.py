from unittest import skip

from django.test import SimpleTestCase

from csss.W3CValidation import W3CValidation


class FroshWeekW3CValidationTest(SimpleTestCase):


    @skip("not ready for w3c validation")
    def test_frosh_2012_page(self):
        W3CValidation().validate_page(path="/events/frosh/2012")

    @skip("not ready for w3c validation")
    def test_frosh_2012_schedule_page(self):
        W3CValidation().validate_page(path="/events/frosh/2012/schedule")

    @skip("not ready for w3c validation")
    def test_frosh_2012_registration_page(self):
        W3CValidation().validate_page(path="/events/frosh/2012/registration")

    @skip("not ready for w3c validation")
    def test_frosh_2012_faq_page(self):
        W3CValidation().validate_page(path="/events/frosh/2012/faq")

    @skip("not ready for w3c validation")
    def test_frosh_2012_contact_page(self):
        W3CValidation().validate_page(path="/events/frosh/2012/contact")

    @skip("not ready for w3c validation")
    def test_frosh_2012_sponsors_page(self):
        W3CValidation().validate_page(path="/events/frosh/2012/sponsors")


    @skip("not ready for w3c validation")
    def test_frosh_2013_page(self):
        W3CValidation().validate_page(path="/events/frosh/2013")

    @skip("not ready for w3c validation")
    def test_frosh_2013_schedule_page(self):
        W3CValidation().validate_page(path="/events/frosh/2013/schedule")

    @skip("not ready for w3c validation")
    def test_frosh_2013_registration_page(self):
        W3CValidation().validate_page(path="/events/frosh/2013/registration")

    @skip("not ready for w3c validation")
    def test_frosh_2013_faq_page(self):
        W3CValidation().validate_page(path="/events/frosh/2013/faq")

    @skip("not ready for w3c validation")
    def test_frosh_2013_contact_page(self):
        W3CValidation().validate_page(path="/events/frosh/2013/contact")

    @skip("not ready for w3c validation")
    def test_frosh_2013_sponsors_page(self):
        W3CValidation().validate_page(path="/events/frosh/2013/sponsors")


    @skip("not ready for w3c validation")
    def test_frosh_2014_page(self):
        W3CValidation().validate_page(path="/events/frosh/2014")

    @skip("not ready for w3c validation")
    def test_frosh_2014_schedule_page(self):
        W3CValidation().validate_page(path="/events/frosh/2014/schedule")

    @skip("not ready for w3c validation")
    def test_frosh_2014_registration_page(self):
        W3CValidation().validate_page(path="/events/frosh/2014/registration")

    @skip("not ready for w3c validation")
    def test_frosh_2014_faq_page(self):
        W3CValidation().validate_page(path="/events/frosh/2014/faq")

    @skip("not ready for w3c validation")
    def test_frosh_2014_contact_page(self):
        W3CValidation().validate_page(path="/events/frosh/2014/contact")

    @skip("not ready for w3c validation")
    def test_frosh_2014_sponsors_page(self):
        W3CValidation().validate_page(path="/events/frosh/2014/sponsors")


    def test_frosh_2015_page(self):
        W3CValidation().validate_page(path="/events/frosh/2015")

    def test_frosh_2015_frosh_page(self):
        W3CValidation().validate_page(path="/events/frosh/2015/frosh")

    @skip("not ready for w3c validation")
    def test_frosh_2015_conditions_page(self):
        W3CValidation().validate_page(path="/events/frosh/2015/conditions")

    @skip("not ready for w3c validation")
    def test_frosh_2015_contact_page(self):
        W3CValidation().validate_page(path="/events/frosh/2015/contact")


    def test_frosh_2016_page(self):
        W3CValidation().validate_page(path="/events/frosh/2016")

    def test_frosh_2016_frosh_page(self):
        W3CValidation().validate_page(path="/events/frosh/2016/frosh")

    @skip("not ready for w3c validation")
    def test_frosh_2016_conditions_page(self):
        W3CValidation().validate_page(path="/events/frosh/2016/conditions")


    def test_frosh_2017_page(self):
        W3CValidation().validate_page(path="/events/frosh/2017")

    @skip("not ready for w3c validation")
    def test_frosh_2017_frosh_page(self):
        W3CValidation().validate_page(path="/events/frosh/2017/frosh")

    @skip("not ready for w3c validation")
    def test_frosh_2017_conditions_page(self):
        W3CValidation().validate_page(path="/events/frosh/2017/conditions")


    def test_frosh_2018_page(self):
        W3CValidation().validate_page(path="/events/frosh/2018")

    @skip("not ready for w3c validation")
    def test_frosh_2018_frosh_page(self):
        W3CValidation().validate_page(path="/events/frosh/2018/frosh")

    @skip("not ready for w3c validation")
    def test_frosh_2018_conditions_page(self):
        W3CValidation().validate_page(path="/events/frosh/2018/conditions")


    @skip("not ready for w3c validation")
    def test_frosh_2019_page(self):
        W3CValidation().validate_page(path="/events/frosh/2019")

    @skip("not ready for w3c validation")
    def test_frosh_2019_frosh_page(self):
        W3CValidation().validate_page(path="/events/frosh/2019/frosh")


    @skip("not ready for w3c validation")
    def test_frosh_2020_page(self):
        W3CValidation().validate_page(path="/events/frosh/2020")

    @skip("not ready for w3c validation")
    def test_frosh_2020_frosh_page(self):
        W3CValidation().validate_page(path="/events/frosh/2020/frosh")


    def test_frosh_2021_page(self):
        W3CValidation().validate_page(path="/events/frosh/2021")

    def test_frosh_2021_frosh_page(self):
        W3CValidation().validate_page(path="/events/frosh/2021/frosh")


    def test_frosh_2022_page(self):
        W3CValidation().validate_page(path="/events/frosh/2022")

    def test_frosh_2022_frosh_page(self):
        W3CValidation().validate_page(path="/events/frosh/2022/frosh")

    @skip("not ready for w3c validation")
    def test_frosh_2022_secret_page(self):
        W3CValidation().validate_page(path="/events/frosh/2022/secret")


    def test_frosh_2023_sponsor_page(self):
        W3CValidation().validate_page(path="/events/frosh/2023/sponsor")

    @skip("This webpage is supposed to return an error 70% of the time, as an easter egg to froshees")
    def test_frosh_2023_secret_page(self):
        W3CValidation().validate_page(path="/events/frosh/2023/secret")


    def test_frosh_main_page(self):
        W3CValidation().validate_page(path="/events/frosh")