from pymongo import MongoClient
from functools import wraps
import logging
import os
from dotenv import load_dotenv

load_dotenv()
class DatabaseConnectionError(Exception):
    pass


def check_connection(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            self.db.client.admin.command("ping")
        except Exception as error:
            logging.error(f"MongoDB Ping Error: {error}",exc_info=True)
            raise DatabaseConnectionError("Internet connection lost.")

        return func(self, *args, **kwargs)
    return wrapper


class MongoDBConnection:
    def __init__(self):
        url = os.getenv("MONGODB_URI")
        if not url:
            raise DatabaseConnectionError("MONGODB_URI not found in .env")
        self.client = MongoClient(
            url,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000,
            socketTimeoutMS=5000
        )
        self.db = self.client[os.getenv("DATABASE_NAME","fingerprint_attendance")]
        
        self.create_collections()
        self.organizations = (self.db["organizations"])
        self.patients = (self.db["patients"])
        self.attendance = (self.db["attendance"])
        self.deleted_patients = (self.db["deleted_patients"])

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

    def verify_organization(self, username, password):
        organization = (self.organizations.find_one({"username": username}))
        if not organization:
            return None
        if organization["password"] != password:
            return None
        return organization