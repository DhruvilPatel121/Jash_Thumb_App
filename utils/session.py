import logging

logger = logging.getLogger(__name__)

class Session:

    organization_id = None
    organization_username = None

    @classmethod
    def login(cls, organization_id, username):
        logger.info("Logging in organization_id=%s username=%s", organization_id, username)
        cls.organization_id = str(organization_id)
        cls.organization_username = username

    @classmethod
    def logout(cls):
        logger.info("Logging out organization_id=%s username=%s", cls.organization_id, cls.organization_username)
        cls.organization_id = None
        cls.organization_username = None

    @classmethod
    def is_logged_in(cls):
        logger.debug("Checking login status organization_id=%s", cls.organization_id)
        return cls.organization_id is not None