from bson import ObjectId
from datetime import datetime 
from utils.session import Session
from database.mongodb_connection import MongoDBConnection
from database.atlas_connection import AtlasConnection
import logging

logger = logging.getLogger(__name__)

class SyncManager:

    def __init__(self):
        logger.info("Initializing SyncManager")
        self.local_db = MongoDBConnection()
        self.atlas_db = AtlasConnection()

    def run(self):
        try:
            self.sync_organizations()
        except Exception as error:
            logger.error("Organization Sync Error", exc_info=True)

        try:
            self.process_outbox()
        except Exception as error:
            logger.error("Outbox Sync Error", exc_info=True)

    def sync_organizations(self):
        logger.info("Running organization sync")
        if not Session.is_logged_in():
            logger.debug("Session not logged in, skipping organization sync")
            return

        organization_id = ObjectId(Session.organization_id)
        local_org = self.local_db.organizations.find_one({"_id": organization_id})
        atlas_org = self.atlas_db.organizations.find_one({"_id": organization_id})
        # print(f"Local Org: {local_org}")
        # print(f"Atlas Org: {atlas_org}")  # Debugging line

        if not local_org or not atlas_org:
            logger.warning("Local or Atlas organization record missing for sync")
            return

        atlas_time = atlas_org.get("updated_at")
        local_time = local_org.get("updated_at")
        # print(f"Local Time: {local_time}")
        # print(f"Atlas Time: {atlas_time}")  # Debugging line

        def get_valid_time(t):
            if isinstance(t, datetime):
                return t
            if isinstance(t, str) and t:
                try:
                    return datetime.fromisoformat(t)
                except ValueError:
                    logger.warning("Invalid datetime format in sync timestamps: %s", t)
                    pass
            return datetime.min 

        atlas_time_dt = get_valid_time(atlas_time)
        local_time_dt = get_valid_time(local_time)

        if atlas_time_dt > local_time_dt:
            self.local_db.organizations.update_one(
                {"_id": organization_id},
                {
                    "$set": {
                        "email": atlas_org.get("email"),
                        "password": atlas_org.get("password"),
                        "name": atlas_org.get("name"),
                        "address": atlas_org.get("address"),
                        "staff_password": atlas_org.get("staff_password"),
                        "is_locked": atlas_org.get("is_locked"),
                        "valid_upto": atlas_org.get("valid_upto"),
                        "updated_at": atlas_time 
                    }
                }
            )
            logger.info("Organization Synced: Atlas -> Local for %s", Session.organization_username)
        elif local_time_dt > atlas_time_dt:
            self.atlas_db.organizations.update_one(
                {"_id": organization_id},
                {
                    "$set": {
                        "password": local_org.get("password"),
                        "staff_password": local_org.get("staff_password"),
                        "updated_at": local_time 
                    }
                }
            )
            logger.info("Organization Synced: Local -> Atlas for %s", Session.organization_username)
        else:
            logger.debug("Organization data already synchronized for %s", Session.organization_username)

    def process_outbox(self):
        logger.info("Processing outbox tasks")
        pending_tasks = list(self.local_db.offline_outbox.find().sort("timestamp", 1))
        
        if not pending_tasks:
            logger.info("No pending outbox tasks to sync")
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
                logger.info("Successfully synced: %s on %s", task["action"], task["collection"])

            except Exception as e:
                logger.error("Sync Outbox Failed: %s", e, exc_info=True)
                break