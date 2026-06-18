class Session:

    organization_id = None
    organization_username = None

    @classmethod
    def login(cls, organization_id, username):
        cls.organization_id = str(organization_id)
        cls.organization_username = username

    @classmethod
    def logout(cls):
        cls.organization_id = None
        cls.organization_username = None

    @classmethod
    def is_logged_in(cls):
        return cls.organization_id is not None