import logging
from datetime import datetime
from PyQt6.QtWidgets import QMessageBox
from database.mongodb_connection import MongoDBConnection
import sys
from bson import ObjectId

logger = logging.getLogger(__name__)

class LicenseManager:

    def __init__(self):
        logger.info("Initializing LicenseManager")
        self.db = MongoDBConnection()
        self.organizations = self.db.organizations

    def check_license_validity(self, organization_id, parent=None):
        logger.info("Checking license validity for organization_id=%s", organization_id)
        try:
            org = self.organizations.find_one({"_id": ObjectId(organization_id)})

            if not org:
                logger.warning("Organization record not found for organization_id=%s", organization_id)
                return True

            valid_upto = org.get("valid_upto")
            logger.debug("Retrieved valid_upto=%s for organization_id=%s", valid_upto, organization_id)

            if not valid_upto:
                logger.debug("No valid_upto value found, assuming license is valid")
                return True

            # Mongo stores ISO string
            if isinstance(valid_upto, str):
                expiry_date = datetime.fromisoformat(
                    valid_upto.replace("Z", "+00:00")
                ).date()
            else:
                expiry_date = valid_upto.date()

            today = datetime.now().date()
            logger.debug("Current date=%s, License expiry date=%s", today, expiry_date)
            if today > expiry_date:
                logger.warning("License expired for organization_id=%s expiry_date=%s", organization_id, expiry_date)
                QMessageBox.critical(
                    parent,
                    "License Expired",
                    "Software license has expired.\nPlease contact Shivvilon Solution."
                )
                return False

            logger.info("License is valid for organization_id=%s", organization_id)
            return True

        except Exception as e:
            logger.error("Error checking license validity", exc_info=True)
            return False