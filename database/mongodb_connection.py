from pymongo import MongoClient
from functools import wraps
import logging

class DatabaseConnectionError(Exception):
    pass


def check_connection(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            self.db.client.admin.command("ping")
        except Exception as error:
            logging.error(f"MongoDB Ping Error: {error}",exc_info=True)
            raise DatabaseConnectionError("Local database is not available.")

        return func(self, *args, **kwargs)
    return wrapper


class MongoDBConnection:
    def __init__(self):
        url = "mongodb://localhost:27017/"
        
        if not url:
            raise DatabaseConnectionError("MONGODB_URI not found")
        self.client = MongoClient(
            url,
            serverSelectionTimeoutMS=500,
            connectTimeoutMS=500,
            socketTimeoutMS=500
        )
        self.db = self.client["fingerprint_attendance"]
        self.create_collections()
        self.organizations = (self.db["organizations"])
        self.patients = (self.db["patients"])
        self.attendance = (self.db["attendance"])
        self.deleted_patients = (self.db["deleted_patients"])
        self.offline_outbox = (self.db["offline_outbox"])

    def create_collections(self):
        collections = (self.db.list_collection_names())
        if "organizations" not in collections:
            self.db.create_collection("organizations")
        if "patients" not in collections:
            self.db.create_collection("patients")
        if "attendance" not in collections:
            self.db.create_collection("attendance")
        if "deleted_patients" not in collections:
            self.db.create_collection("deleted_patients")
        if "offline_outbox" not in collections:
            self.db.create_collection("offline_outbox")

    def verify_organization(self, username, password):
        organization = (self.organizations.find_one({"username": username}))
        if not organization:
            return None
        if organization["password"] != password:
            return None
        return organization