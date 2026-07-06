import logging
import socket
from pymongo import MongoClient

logger = logging.getLogger(__name__)

def internet_available(timeout=1):
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=timeout)
        return True
    except OSError:
        return False

class AtlasConnection:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AtlasConnection, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self.url = (
            "mongodb+srv://shivvilonsolution:"
            "eLoXWGiHrrSwsNID@thumbscanner.4nd2iio.mongodb.net/"
            "?appName=thumbscanner"
        )
        self.client = None
        self.db = None
        self.organizations = None
        self.patients = None
        self.attendance = None
        self.deleted_patients = None

    def connect(self):
        if not internet_available():
            logger.warning("No internet available; skipping Atlas connection")
            return False

        if self.client is not None:
            return True

        try:
            self.client = MongoClient(
                self.url,
                connectTimeoutMS=10000,
                serverSelectionTimeoutMS=10000,
                socketTimeoutMS=10000
            )
            self.db = self.client["fingerprint_attendance"]
            self.organizations = self.db["organizations"]
            self.patients = self.db["patients"]
            self.attendance = self.db["attendance"]
            self.deleted_patients = self.db["deleted_patients"]
            logger.info("Atlas Connected Successfully")
            return True
        except Exception:
            logger.error("Atlas Connection Error", exc_info=True)
            self.client = None
            self.db = None
            self.organizations = None
            self.patients = None
            self.attendance = None
            self.deleted_patients = None
            return False

    def is_connected(self):
        if not self.connect():
            return False
        try:
            self.client.admin.command("ping")
            return True
        except Exception:
            logger.error("Atlas connection ping failed", exc_info=True)
            self.client = None
            self.db = None
            return False