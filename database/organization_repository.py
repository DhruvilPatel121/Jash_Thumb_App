from database.mongodb_connection import MongoDBConnection
from bson import ObjectId
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class OrganizationRepository:

    def __init__(self):
        logger.info("Initializing OrganizationRepository")
        self.db = MongoDBConnection()
        self.organizations = (self.db.organizations)

    def get_by_email(self,email):
        logger.info("Getting organization by email: %s", email)
        email = self.organizations.find_one({"email": email})
        return email

    def email_exists(self,email):
        logger.info("Checking if email exists: %s", email)
        organization = (self.get_by_email(email))
        return organization is not None

    def verify_login(self,email,password):
        logger.info("Verifying login for email: %s", email)
        organization = (self.get_by_email(email))
        # print(f"Organization found: {password}")  # Debugging line
        # print(f"Organization found: {organization['password']}")  # Debugging line
        if not organization:
            return None
        if organization["password"] != password:
            return None
        return organization
 
    def verify_role_password(self, organization_id, hashed_password):
        logger.info("Verifying role password for organization_id: %s", organization_id)
        organization = self.organizations.find_one({"_id": ObjectId(organization_id)})
        if not organization:
            logger.warning("Organization not found for role verification: %s", organization_id)
            return False
        # print(f"Organization found for role verification: {organization['password']}")  # Debugging line
        # print(f"Provided hashed password: {hashed_password}")  # Debugging line
        return organization.get("password") == hashed_password

    def get_by_id(self, organization_id):
        logger.info("Retrieving organization by id: %s", organization_id)
        return self.organizations.find_one({"_id": ObjectId(organization_id)})
    
    def update_admin_password(self, organization_id, new_hashed_password):
        logger.info("Updating admin password for organization_id: %s", organization_id)
        try:
            current_time = datetime.now().isoformat()
            result = self.organizations.update_one(
                {"_id": ObjectId(organization_id)},
                {"$set": {
                    "password": new_hashed_password,
                    "updated_at": current_time
                }}
            )
            return result.matched_count > 0
        except Exception as e:
            logger.error("Error updating admin password", exc_info=True)
            return False