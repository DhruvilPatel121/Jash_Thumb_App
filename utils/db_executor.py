# utils/db_executor.py

import logging
from datetime import datetime
from database.mongodb_connection import MongoDBConnection
from database.atlas_connection import AtlasConnection

class DBExecutor:
    def __init__(self):
        self.local = MongoDBConnection()
        self.atlas = AtlasConnection()

    def execute(self, action, collection_name, data_or_query, update_data=None):

        # ==========================================
        # 1. ACTION: INSERT
        # ==========================================
        if action == "INSERT":
            # Pehla hamesha Local DB ma insert karo (Jethi app fast chale)
            result = self.local.db[collection_name].insert_one(data_or_query)
            inserted_id = result.inserted_id
            
            try:
                if self.atlas.is_connected():
                    # Local ane Atlas ma same ID rahe e jaruri che
                    data_or_query["_id"] = inserted_id 
                    self.atlas.db[collection_name].insert_one(data_or_query)
                    return inserted_id
            except Exception as e:
                logging.warning(f"Atlas offline during INSERT. Saving to Outbox: {e}")
            
            # Jo Atlas fail thay (Net bandh che), to Outbox ma entry lakho
            self._save_to_outbox("INSERT", collection_name, {"_id": inserted_id}, data_or_query)
            return inserted_id

        # ==========================================
        # 2. ACTION: UPDATE
        # ==========================================
        elif action == "UPDATE":
            # Local Update
            self.local.db[collection_name].update_many(data_or_query, update_data)
            
            # Atlas Update Try
            try:
                if self.atlas.is_connected():
                    self.atlas.db[collection_name].update_many(data_or_query, update_data)
                    return True
            except Exception as e:
                logging.warning(f"Atlas offline during UPDATE. Saving to Outbox: {e}")
                
            # Fallback
            self._save_to_outbox("UPDATE", collection_name, data_or_query, update_data)
            return True

        # ==========================================
        # 3. ACTION: DELETE
        # ==========================================
        elif action == "DELETE":
            # Local Delete
            self.local.db[collection_name].delete_one(data_or_query)
            
            # Atlas Delete Try
            try:
                if self.atlas.is_connected():
                    self.atlas.db[collection_name].delete_one(data_or_query)
                    return True
            except Exception as e:
                logging.warning(f"Atlas offline during DELETE. Saving to Outbox: {e}")
                
            # Fallback
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
        logging.info(f"Saved {action} operation to offline_outbox for {collection_name}")