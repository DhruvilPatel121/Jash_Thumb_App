from pymongo import MongoClient
from functools import wraps
import logging

logger = logging.getLogger(__name__)

class DatabaseConnectionError(Exception):
    pass


def check_connection(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            self.db.client.admin.command("ping")
        except Exception as error:
            logger.error("MongoDB Ping Error", exc_info=True)
            raise DatabaseConnectionError("Local database is not available.")

        return func(self, *args, **kwargs)
    return wrapper


class MongoDBConnection:
    def __init__(self):
        logger.info("Initializing MongoDBConnection")
        url = "mongodb://localhost:27017/"

        if not url:
            logger.error("MONGODB_URI not found")
            raise DatabaseConnectionError("MONGODB_URI not found")

        logger.debug("Creating MongoDB client with URL")
        self.client = MongoClient(
            url,
            serverSelectionTimeoutMS=500,
            connectTimeoutMS=500,
            socketTimeoutMS=500
        )
        logger.info("MongoDB client initialized successfully")

        self.db = self.client["fingerprint_attendance"]
        self.create_collections()
        self.organizations = (self.db["organizations"])
        self.patients = (self.db["patients"])
        self.attendance = (self.db["attendance"])
        self.deleted_patients = (self.db["deleted_patients"])
        self.offline_outbox = (self.db["offline_outbox"])

    def create_collections(self):
        logger.info("Ensuring required MongoDB collections exist")
        collections = (self.db.list_collection_names())
        logger.debug("Existing MongoDB collections: %s", collections)

        if "organizations" not in collections:
            logger.debug("Creating missing collection: organizations")
            self.db.create_collection("organizations")
        if "patients" not in collections:
            logger.debug("Creating missing collection: patients")
            self.db.create_collection("patients")
        if "attendance" not in collections:
            logger.debug("Creating missing collection: attendance")
            self.db.create_collection("attendance")
        if "deleted_patients" not in collections:
            logger.debug("Creating missing collection: deleted_patients")
            self.db.create_collection("deleted_patients")
        if "offline_outbox" not in collections:
            logger.debug("Creating missing collection: offline_outbox")
            self.db.create_collection("offline_outbox")

    def verify_organization(self, username, password):
        logger.info("Verifying organization credentials for username=%s", username)
        organization = (self.organizations.find_one({"username": username}))
        if not organization:
            logger.warning("Organization not found for username=%s", username)
            return None
        if organization["password"] != password:
            logger.warning("Organization password mismatch for username=%s", username)
            return None
        return organization