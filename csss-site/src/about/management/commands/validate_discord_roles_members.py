import json
import time
from copy import deepcopy

from django.core.management import BaseCommand
from django.db.models import Q

from about.models import Officer, UnProcessedOfficer, OfficerEmailListAndPositionMapping
from about.views.commands.validate_discord_roles_members.determine_changes_for_exec_discord_group_role_validation \
    import determine_changes_for_exec_discord_group_role_validation
from about.views.commands.validate_discord_roles_members. \
    determine_changes_for_position_specific_discord_role_validation import \
    determine_changes_for_position_specific_discord_role_validation
from about.views.commands.validate_discord_roles_members.get_all_user_dictionaries import get_all_user_dictionaries
from about.views.commands.validate_discord_roles_members.get_role_dictionary import get_role_dictionary
from about.views.input_new_officers.enter_new_officer_info.grant_digital_resource_access.assign_discord_roles import \
    EXEC_DISCORD_ROLE_NAME, get_discord_guild_roles, assign_roles_to_officer
from csss.models import CronJob, CronJobRunStat
from csss.setup_logger import Loggers
from csss.views_helper import get_current_term_obj, get_previous_term_obj

SERVICE_NAME = "validate_discord_roles_members"


class Command(BaseCommand):
    help = "Ensure that the Discord Roles associated with the Officers have valid members"

    def handle(self, *args, **options):
        time1 = time.perf_counter()
        logger = Loggers.get_logger(logger_name=SERVICE_NAME)
        current_officers = Officer.objects.all().filter(
            elected_term=get_current_term_obj()
        )
        officers_to_ignore = list(UnProcessedOfficer.objects.all().values_list('sfu_computing_id', flat=True))
        if len((deepcopy(current_officers).filter(position_name__contains="Executive at Large"))) == 0:
            current_officers = Officer.objects.filter(
                (
                    Q(elected_term=get_current_term_obj()) &
                    ~Q(sfu_computing_id__in=officers_to_ignore)
                )
                |
                (
                    Q(elected_term=get_previous_term_obj()) &
                    Q(position_name__contains="Executive at Large") &
                    ~Q(sfu_computing_id__in=officers_to_ignore)
                )
            )
        else:
            current_officers = Officer.objects.filter(
                (
                    Q(elected_term=get_current_term_obj()) &
                    ~Q(sfu_computing_id__in=officers_to_ignore)
                )
            )
        officer_discord_id__officer_full_name = {
            officer.discord_id: officer.full_name for officer in current_officers
        }
        position_infos = OfficerEmailListAndPositionMapping.objects.all()

        success, error_message, role_id__list_of_users, user_id__user_obj = get_all_user_dictionaries()
        if not success:
            logger.info(
                f"[about/validate_discord_roles_members.py() Command() ] {error_message}  "
            )
            return
        success, error_message, role_id__role = get_role_dictionary()
        if not success:
            logger.info(
                f"[about/validate_discord_roles_members.py() Command() ] {error_message}  "
            )
            return
        discord_role_names = [
            position_info.discord_role_name
            for position_info in position_infos
        ]
        discord_role_names.append(EXEC_DISCORD_ROLE_NAME)
        success, error_message, matching_executive_roles = get_discord_guild_roles(discord_role_names)
        if not success:
            logger.info(
                f"[about/validate_discord_roles_members.py() Command() ] {error_message}  "
            )
            return

        exec_discord_role_id = matching_executive_roles[EXEC_DISCORD_ROLE_NAME]['id'] \
            if EXEC_DISCORD_ROLE_NAME in matching_executive_roles else None
        if exec_discord_role_id is None:
            logger.info(
                f"[about/validate_discord_roles_members.py() Command() ] unable to get the role_id for "
                f"the discord group \"{EXEC_DISCORD_ROLE_NAME}\" role"
            )
        else:
            del matching_executive_roles[EXEC_DISCORD_ROLE_NAME]

        members_id__role_ids = {}  # current officer
        discord_id_for_users_that_should_be_in_exec_discord_group_role = []
        determine_changes_for_position_specific_discord_role_validation(
            user_id__user_obj, role_id__list_of_users, role_id__role, officer_discord_id__officer_full_name,
            exec_discord_role_id, members_id__role_ids,
            discord_id_for_users_that_should_be_in_exec_discord_group_role, position_infos,
            matching_executive_roles, current_officers
        )
        determine_changes_for_exec_discord_group_role_validation(
            user_id__user_obj, role_id__list_of_users, role_id__role, members_id__role_ids,
            discord_id_for_users_that_should_be_in_exec_discord_group_role, exec_discord_role_id
        )

        logger.info(
            "[about/validate_discord_roles_members.py() Command() ] final permission change of "
            f"{json.dumps(members_id__role_ids, indent=3)}"
        )
        for discord_id, user_role_info in members_id__role_ids.items():
            logger.info(
                f"[about/validate_discord_roles_members.py() Command() ] setting discord roles for"
                f" {user_role_info['username']}({discord_id})"
            )
            success, error_message = assign_roles_to_officer(
                discord_id,
                [role_id for role_name, role_id in user_role_info['roles'].items()]
            )
            if not success:
                logger.error(f"[about/validate_discord_roles_members.py() Command() ] {error_message}")
        time2 = time.perf_counter()
        total_seconds = time2 - time1
        cron_job = CronJob.objects.get(job_name=SERVICE_NAME)
        number_of_stats = CronJobRunStat.objects.all().filter(job=cron_job)
        if len(number_of_stats) == 10:
            first = number_of_stats.order_by('id').first()
            if first is not None:
                first.delete()
        CronJobRunStat(job=cron_job, run_time_in_seconds=total_seconds).save()
        Loggers.remove_logger(SERVICE_NAME)
