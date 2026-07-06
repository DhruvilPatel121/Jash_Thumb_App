# utils/db_executor.py

import logging
from datetime import datetime
from database.mongodb_connection import MongoDBConnection
from database.atlas_connection import AtlasConnection

logger = logging.getLogger(__name__)

class DBExecutor:
    def __init__(self):
        logger.info("Initializing DBExecutor")
        self.local = MongoDBConnection()
        self.atlas = AtlasConnection()

    def execute(self, action, collection_name, data_or_query, update_data=None):
        logger.info("Executing DB action=%s on collection=%s", action, collection_name)

        if action == "INSERT":
            logger.debug("Performing local INSERT for collection=%s", collection_name)
            result = self.local.db[collection_name].insert_one(data_or_query)
            inserted_id = result.inserted_id
            
            try:
                if self.atlas.is_connected():
                    data_or_query["_id"] = inserted_id 
                    self.atlas.db[collection_name].insert_one(data_or_query)
                    return inserted_id
            except Exception as e:
                logger.warning("Atlas offline during INSERT. Saving to Outbox: %s", e)
                logger.error("INSERT operation failed on Atlas", exc_info=True)
            
            self._save_to_outbox("INSERT", collection_name, {"_id": inserted_id}, data_or_query)
            return inserted_id

        elif action == "UPDATE":
            logger.debug("Performing local UPDATE for collection=%s", collection_name)
            self.local.db[collection_name].update_many(data_or_query, update_data)
            
            try:
                if self.atlas.is_connected():
                    self.atlas.db[collection_name].update_many(data_or_query, update_data)
                    return True
            except Exception as e:
                logger.warning("Atlas offline during UPDATE. Saving to Outbox: %s", e)
                logger.error("UPDATE operation failed on Atlas", exc_info=True)
                
            self._save_to_outbox("UPDATE", collection_name, data_or_query, update_data)
            return True

        elif action == "DELETE":
            logger.debug("Performing local DELETE for collection=%s", collection_name)
            self.local.db[collection_name].delete_one(data_or_query)
            
            try:
                if self.atlas.is_connected():
                    self.atlas.db[collection_name].delete_one(data_or_query)
                    return True
            except Exception as e:
                logger.warning("Atlas offline during DELETE. Saving to Outbox: %s", e)
                logger.error("DELETE operation failed on Atlas", exc_info=True)
                
            self._save_to_outbox("DELETE", collection_name, data_or_query, None)
            return True

    def _save_to_outbox(self, action, collection_name, query, data):
        outbox_entry = {
            "action": action,
            "collection": collection_name,
            "query": query,
            "data": data,
            "timestamp": datetime.now()
        }
        self.local.db["offline_outbox"].insert_one(outbox_entry)
        logger.info("Saved %s operation to offline_outbox for %s", action, collection_name)