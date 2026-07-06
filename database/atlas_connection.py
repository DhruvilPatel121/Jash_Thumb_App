from pymongo import MongoClient
import logging

logger = logging.getLogger(__name__)


class AtlasConnection:
    _instance = None

    def __new__(cls):
        logger.info("Creating AtlasConnection singleton instance")
        if cls._instance is None:
            cls._instance = super(AtlasConnection, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        logger.info("Initializing AtlasConnection internal state")
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
        logger.info("Connecting to Atlas MongoDB")
        try:
            if self.client is not None:
                logger.debug("Atlas client already initialized, reusing existing connection")
                return True

            self.client = MongoClient(
                self.url,
                connectTimeoutMS=10000,
                serverSelectionTimeoutMS=2000,
                socketTimeoutMS=10000
            )

            # Force connection
            self.client.admin.command("ping")

            self.db = self.client["fingerprint_attendance"]

            self.organizations = self.db["organizations"]
            self.patients = self.db["patients"]
            self.attendance = self.db["attendance"]
            self.deleted_patients = self.db["deleted_patients"]

            logger.info("Atlas Connected Successfully")
            return True

        except Exception as error:
            logger.error("Atlas Connection Error", exc_info=True)

            self.client = None
            self.db = None
            self.organizations = None
            self.patients = None
            self.attendance = None
            self.deleted_patients = None

            return False

    def is_connected(self):
        logger.info("Checking Atlas connection status")
        try:
            if not self.connect():
                logger.warning("Atlas connection check failed during connect")
                return False

            self.client.admin.command("ping")
            return True

        except Exception:
            logger.error("Atlas connection ping failed", exc_info=True)
            self.client = None
            self.db = None
            return False