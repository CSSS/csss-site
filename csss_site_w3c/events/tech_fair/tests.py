from django.test import SimpleTestCase

from csss.W3CValidation import W3CValidation


class TechFairW3CValidationTest(SimpleTestCase):

    def test_tech_fair_2022_page(self):
        W3CValidation().validate_page(path="/events/tech_fair/2022")


    def test_tech_fair_2022_main_page(self):
        W3CValidation().validate_page(path="/events/tech_fair/2022/main")


    def test_tech_fair_2023_page(self):
        W3CValidation().validate_page(path="/events/tech_fair/2023")


    def test_tech_fair_2023_company_package_page(self):
        W3CValidation().validate_page(path="/events/tech_fair/2023/company_package")
