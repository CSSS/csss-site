from django.http import HttpResponseRedirect
from django.shortcuts import render

from csss.models import CSSSError
from csss.views.context_creation.create_authenticated_contexts import create_context_for_displaying_errors

ERROR_FILE_TO_DISPLAY_KEY = 'file_key'
ERROR_FILE_TO_DISPLAY_VALUE = 'file'

ERROR_FILES_TO_DELETE_KEY = 'file_to_delete_key'
ERROR_FILES_TO_DELETE_VALUE = 'file_to_delete'

TOGGLE_ERROR_FILE_FIXED_KEY = 'mark_to_toggle_fixed_key'
TOGGLE_ERROR_FILE_FIXED_VALUE = 'mark_to_toggle'


def index(request):
    context = create_context_for_displaying_errors(request, 'errors')
    errors = CSSSError.objects.all().exclude(
        message="Couldn't do oauth2 because Install python-social-auth to use oauth2 auth for gmail\n"
    )
    if ERROR_FILE_TO_DISPLAY_VALUE in request.GET:
        file_id = request.GET[ERROR_FILE_TO_DISPLAY_VALUE]
        csss_error = errors.get(id=file_id)
        context["error_file"] = open(f"{csss_error.get_error_absolute_path}", 'rb').read().decode("UTF-8")
        context["debug_file"] = open(f"{csss_error.get_debug_absolute_path}", 'rb').read().decode("UTF-8")
        context['marker_string'] = "Mark File as Not Fixed" if csss_error.fixed else 'Mark Files as Fixed'
        context['csss_error_id'] = file_id
    else:
        if ERROR_FILES_TO_DELETE_VALUE in request.GET:
            error_belonging_to_file = errors.get(id=request.GET[ERROR_FILES_TO_DELETE_VALUE])
            errors.filter(
                file_path=error_belonging_to_file.file_path, filename=error_belonging_to_file.filename
            ).delete()
            return HttpResponseRedirect(request.path)
        if TOGGLE_ERROR_FILE_FIXED_VALUE in request.GET:
            error_belonging_to_file = errors.get(id=request.GET[TOGGLE_ERROR_FILE_FIXED_VALUE])
            fixed_errors = errors.filter(
                file_path=error_belonging_to_file.file_path, filename=error_belonging_to_file.filename
            )
            for fixed_error in fixed_errors:
                fixed_error.fixed = not fixed_error.fixed
            CSSSError.objects.bulk_update(fixed_errors, ['fixed'])
            return HttpResponseRedirect(request.path)
        un_fixed_errors = CSSSError.objects.all().exclude(
            message="Couldn't do oauth2 because Install python-social-auth to use oauth2 auth for gmail\n"
        ).filter(fixed=False)
        un_fixed_errors = list({error.get_error_project_path: error for error in un_fixed_errors}.values())
        context['csss_errors'] = un_fixed_errors
        fixed_errors = CSSSError.objects.all().exclude(
            message="Couldn't do oauth2 because Install python-social-auth to use oauth2 auth for gmail\n"
        ).filter(fixed=True)
        fixed_errors = list({error.get_error_project_path: error for error in fixed_errors}.values())
        context['csss_fixed_errors'] = fixed_errors
    context.update({
        ERROR_FILE_TO_DISPLAY_KEY: ERROR_FILE_TO_DISPLAY_VALUE,
        ERROR_FILES_TO_DELETE_KEY: ERROR_FILES_TO_DELETE_VALUE,
        TOGGLE_ERROR_FILE_FIXED_KEY: TOGGLE_ERROR_FILE_FIXED_VALUE
    })
    return render(request, 'csss/errors/index.html', context)
