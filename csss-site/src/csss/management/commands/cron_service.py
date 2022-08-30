from django.core.management import BaseCommand


class Command(BaseCommand):

    def handle(self, **options):
        print("cron service")
