from pymongo import MongoClient
import logging


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
        try:
            if self.client is not None:
                return True

            self.client = MongoClient(
                self.url,
                serverSelectionTimeoutMS=500,
                connectTimeoutMS=500,
                socketTimeoutMS=500
            )

            # Force connection
            self.client.admin.command("ping")

            self.db = self.client["fingerprint_attendance"]

            self.organizations = self.db["organizations"]
            self.patients = self.db["patients"]
            self.attendance = self.db["attendance"]
            self.deleted_patients = self.db["deleted_patients"]

            logging.info("Atlas Connected Successfully")
            return True

        except Exception as error:
            logging.error(
                f"Atlas Connection Error: {error}",
                exc_info=True
            )

            self.client = None
            self.db = None
            self.organizations = None
            self.patients = None
            self.attendance = None
            self.deleted_patients = None

            return False

    def is_connected(self):
        try:
            if not self.connect():
                return False

            self.client.admin.command("ping")
            return True

        except Exception:
            self.client = None
            self.db = None
            return False