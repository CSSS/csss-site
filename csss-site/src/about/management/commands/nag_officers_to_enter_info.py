from django.core.management import BaseCommand

from about.views.commands.nag_officers_to_enter_info import run_job


class Command(BaseCommand):
    help = "nag any officers who have not entered their info"

    def handle(self, *args, **options):
        run_job()
