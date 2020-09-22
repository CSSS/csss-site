import gitlab
import logging

logger = logging.getLogger('csss_site')


class GitLabAPI:
    def __init__(self, private_token):
        self.connection_successful = False
        self.error_message = None
        if private_token is None:
            self.error_message = "private_token is not valid"
            logger.error(f"[GitLabAPI __init__()] {self.error_message}")
            return
        try:
            self.sfu_gitlab = gitlab.Gitlab(url="https://csil-git1.cs.surrey.sfu.ca", private_token=private_token)
            self.connection_successful = True
        except Exception as e:
            self.error_message = f"experienced following error when trying to connect to SFU Gitlab :\n{e}"
            logger.error(f"[GitLabAPI __init__()] {self.error_message}")

    def add_officer_to_csss_group(self, users):
        """Add listed users to the CSSS group

        Keyword Arguments:
        users -- a list of all the users who need to be added to the group

        return
        success -- true or false Bool
        error_message -- error message if success is False, None otherwise
        """
        if self.connection_successful:
            try:
                csss_group = [group for group in self.sfu_gitlab.groups.list() if group.name == "CSSS"][0]
            except Exception as e:
                logger.error(
                    "[GitLabAPI add_officer_to_csss_group()] experienced following error when"
                    f" getting the \"CSSS\" group\n{e}"
                )
                return False, "Unable to get the CSSS SFU Gitlab group"

            for user_name in users:
                try:
                    user = None
                    try:
                        user = self.sfu_gitlab.users.list(username=f'{user_name}')[0]
                    except Exception as e:
                        logger.error(
                            f"[GitLabAPI add_officer_to_csss_group()] unable to get the user {user} "
                            f"due to {e}"
                        )
                    if user is not None:
                        user_membership = [
                            membership for membership in csss_group.members.list()
                            if membership.username == user.username
                        ]
                        if len(user_membership) > 0:
                            if user_membership[0].access_level != gitlab.DEVELOPER_ACCESS:
                                user_membership[0].access_level = gitlab.DEVELOPER_ACCESS
                                user_membership[0].save()
                                logger.info(
                                    f"[GitLabAPI add_officer_to_csss_group()] updating the permission"
                                    f" for user {user.username} to developer level"
                                )
                            else:
                                logger.info(
                                    f"[GitLabAPI add_officer_to_csss_group()] user {user.username} already"
                                    f" had access to the CSSS group at developer level"
                                )
                                continue
                        else:
                            csss_group.members.create({'user_id': user.id, 'access_level': gitlab.DEVELOPER_ACCESS})
                            logger.info(
                                f"[GitLabAPI add_officer_to_csss_group()] added user {user.username} "
                                f"to SFU Gitlab CSSS group"
                            )
                except Exception as e:
                    error_message = f"experienced the following error when adding user {user_name} " \
                                    f"to the SFU CSSS Gitlab Group\n{e}"
                    logger.error(f"[GitLabAPI add_officer_to_csss_group()] {error_message}")
                    return False, error_message
            return True, None

    def remove_user_from_group(self, users):
        """Removes the listed user from the SFU CSSS gitlab org

        Keyword Arguments:
        users -- a list of all the users who need to be removed from the group

        """
        if self.connection_successful:
            try:
                csss_group = [group for group in self.sfu_gitlab.groups.list() if group.name == "CSSS"][0]
            except Exception as e:
                logger.error(
                    "[GitLabAPI remove_user_from_group()] experienced following error when"
                    f" getting the \"CSSS\" group\n{e}"
                )
                return False, "Unable to get the CSSS SFU Gitlab group"
            for user_name in users:
                try:
                    user = self.sfu_gitlab.users.list(username=f'{user_name}')
                    if len(user) == 0:
                        logger.info(
                            f"[GitLabAPI remove_user_from_group()] user {user_name} "
                            f"does not exist"
                        )
                    else:
                        user = user[0]
                        if len(
                                [member for member in csss_group.members.list() if member.username == user.username]
                        ) > 0:
                            csss_group.members.delete(id=user.id)
                            logger.info(
                                f"[GitLabAPI remove_user_from_group()] removed user {user.username} "
                                f"from SFU Gitlab CSSS group"
                            )
                        else:
                            logger.info(
                                f"[GitLabAPI remove_user_from_group()] user {user.username} "
                                f"is not in SFU Gitlab CSSS group"
                            )
                except Exception as e:
                    logger.error(
                        "[GitLabAPI remove_user_from_group()] experienced the following error when"
                        f" removing user {user_name} to the SFU CSSS Gitlab Group\n{e}"
                    )
            return True, None

    def ensure_proper_membership(self, users):
        """Ensure that the correct users have access to the SFU CSSS Gitlab on SFU Gitlab

        Keyword Arguments
        users -- a list of sfuids that lists all the memberships that need to be set
        """
        success, error_message = self.add_officer_to_csss_group(users)
        if not success:
            return success, error_message
        if self.connection_successful:
            try:
                csss_group = [group for group in self.sfu_gitlab.groups.list() if group.name == "CSSS"][0]
            except Exception as e:
                logger.error(
                    "[GitLabAPI add_officer_to_csss_group()] experienced following error when"
                    f" getting the \"CSSS\" group\n{e}"
                )
                return False, "Unable to get the CSSS SFU Gitlab group"
            for membership in csss_group.members.list():
                if len([
                    user for user in users if user.username == membership.username
                ]) == 0:
                    self.remove_user_from_group([membership.username])
