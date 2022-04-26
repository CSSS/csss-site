from django.conf import settings

from resource_management.views.resource_apis.github.github_api import GitHubAPI


def validate_github_username(github_username=None):
    if github_username is None:
        return False, "No github username specified"
    github_api = GitHubAPI(settings.GITHUB_ACCESS_TOKEN)
    success, error_message = github_api.validate_user(github_username)
    if not success:
        return success, error_message
    return github_api.verify_user_in_org(github_username, invite_user=True)
