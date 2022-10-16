from resource_management.views.resource_views import validate_google_drive, validate_github


def run_job():
    validate_google_drive()
    validate_github()
