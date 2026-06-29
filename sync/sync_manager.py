from bson import ObjectId
from utils.session import Session
from database.mongodb_connection import MongoDBConnection
from database.atlas_connection import AtlasConnection
import logging

class SyncManager:

    def __init__(self):
        self.local_db = MongoDBConnection()
        self.atlas_db = AtlasConnection()

    def run(self):
        try:
            self.sync_organizations()
        except Exception as error:
            logging.error(f"Organization Sync Error: {error}", exc_info=True)

        try:
            self.process_outbox()
        except Exception as error:
            logging.error(f"Outbox Sync Error: {error}", exc_info=True)

    def sync_organizations(self):
        if not Session.is_logged_in():
            return

        organization_id = ObjectId(Session.organization_id)
        local_org = self.local_db.organizations.find_one({"_id": organization_id})
        atlas_org = self.atlas_db.organizations.find_one({"_id": organization_id})

        if not local_org or not atlas_org:
            return

        atlas_time = atlas_org.get("updated_at", "")
        local_time = local_org.get("updated_at", "")

        # 1. Jo Atlas ma data latest hoy, to Local (Compass) update karo
        if atlas_time > local_time:
            self.local_db.organizations.update_one(
                {"_id": organization_id},
                {
                    "$set": {
                        "email": atlas_org.get("email"),
                        "password": atlas_org.get("password"),
                        "staff_password": atlas_org.get("staff_password"),
                        "is_locked": atlas_org.get("is_locked"),
                        "updated_at": atlas_time
                    }
                }
            )
            logging.info(f"Organization Synced: Atlas -> Local for {Session.organization_username}")

        # 2. Jo Local (Compass) ma data latest hoy, to Atlas update karo
        elif local_time > atlas_time:
            self.atlas_db.organizations.update_one(
                {"_id": organization_id},
                {
                    "$set": {
                        "email": local_org.get("email"),
                        "password": local_org.get("password"),
                        "staff_password": local_org.get("staff_password"),
                        "is_locked": local_org.get("is_locked"),
                        "updated_at": local_time
                    }
                }
            )
            logging.info(f"Organization Synced: Local -> Atlas for {Session.organization_username}")
            
        # Jo banne no time same hase, to aagal kai nai thay (return thai jase).

    def process_outbox(self):
        pending_tasks = list(self.local_db.offline_outbox.find().sort("timestamp", 1))
        
        if not pending_tasks:
            return 
            
        for task in pending_tasks:
            try:
                col = self.atlas_db.db[task["collection"]]
                
                if task["action"] == "INSERT":
                    col.insert_one(task["data"])
                    
                elif task["action"] == "UPDATE":
                    col.update_many(task["query"], task["data"])
                    
                elif task["action"] == "DELETE":
                    col.delete_one(task["query"])
                    
                self.local_db.offline_outbox.delete_one({"_id": task["_id"]})
                logging.info(f"Successfully synced: {task['action']} on {task['collection']}")

            except Exception as e:
                logging.error(f"Sync Outbox Failed: {e}")
                break