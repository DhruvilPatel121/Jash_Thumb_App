from database.mongodb_connection import MongoDBConnection
from bson import ObjectId
from datetime import datetime

class OrganizationRepository:

    def __init__(self):
        self.db = MongoDBConnection()
        self.organizations = (self.db.organizations)

    def get_by_email(self,email):
        email = self.organizations.find_one({"email": email})
        return email

    def email_exists(self,email):
        organization = (self.get_by_email(email))
        return organization is not None

    def verify_login(self,email,password):
        organization = (self.get_by_email(email))
        if not organization:
            return None
        if organization["password"] != password:
            return None
        return organization
 
    def verify_role_password(self, organization_id, hashed_password):
        organization = self.organizations.find_one({"_id": ObjectId(organization_id)})
        if not organization:
            return None

        # Admin Password
        if organization.get("password") == hashed_password:
            return "Admin"

        # Staff Password
        if organization.get("staff_password") == hashed_password:
            return "Staff"

        return None


    def get_by_id(self, organization_id):
        return self.organizations.find_one({"_id": ObjectId(organization_id)})
    
    def update_admin_password(self, organization_id, new_hashed_password):
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
            print(f"Error updating admin password: {e}")
            return False