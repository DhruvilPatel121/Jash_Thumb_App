from database.mongodb_connection import MongoDBConnection


class OrganizationRepository:

    def __init__(self):
        self.db = MongoDBConnection()
        self.organizations = (self.db.organizations)

    def get_by_username(self,username):
        username = self.organizations.find_one({"email": username})
        return username

    def username_exists(self,username):
        organization = (self.get_by_username(username))
        return organization is not None

    def verify_login(self,username,password):
        organization = (self.get_by_username(username))
        if not organization:
            return None
        if organization["password"] != password:
            return None
        return organization