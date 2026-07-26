# from datetime import datetime
# from PyQt6.QtWidgets import QMessageBox
# import sys
# from database.mongodb_connection import MongoDBConnection


# class LicenseManager:
#     @staticmethod

#     def __init__(self):
#         self.db = MongoDBConnection()
#         self.organizations = self.db.organizations

#     def check_software_expiry(self, organization_id, parent_window=None):
#         try:
#             # 1. Database madhun organization cha data ghya
#             org_data = self.organizations.find_one({"_id": organization_id})
            
#             # Jar database madhye 'valid_upto' field asel tarach check kara
#             if org_data and "valid_upto" in org_data:
#                 expiry_date_str = org_data["valid_upto"]
#                 print(f"Expiry Date from DB: {expiry_date_str}")  # Debugging line
#                 expiry_date = datetime.strptime(expiry_date_str, "%Y-%m-%d")
#                 current_date = datetime.now()
                
#                 # Divsancha farak (difference) kadha
#                 days_left = (expiry_date - current_date).days
                
#                 if days_left < 0:
#                     # Jar divas 0 peksha kami asel tar software band kara
#                     QMessageBox.critical(
#                         parent_window, 
#                         "Software Expired", 
#                         "Tumche software license expire jhale aahe. Krupaya Shivvilon Solution shi sampark sadha."
#                     )
#                     sys.exit() # He line software la thithech band karel
                    
#                 elif days_left <= 15:
#                     # 15 divas baki asel tar warning dya
#                     QMessageBox.warning(
#                         parent_window, 
#                         "License Expiring Soon", 
#                         f"Tumche license {days_left} divsat expire hoil. Velevar renew kara."
#                     )
#         except Exception as e:
#             print(f"Expiry check error: {e}")

from datetime import datetime
from PyQt6.QtWidgets import QMessageBox
from database.mongodb_connection import MongoDBConnection
import sys
from bson import ObjectId

class LicenseManager:

    def __init__(self):
        self.db = MongoDBConnection()
        self.organizations = self.db.organizations

    def check_license_validity(self, organization_id, parent=None):
        try:
            org = self.organizations.find_one({"_id": ObjectId(organization_id)})

            if not org:
                return True

            valid_upto = org.get("valid_upto")

            if not valid_upto:
                return True

            # Mongo stores ISO string
            if isinstance(valid_upto, str):
                expiry_date = datetime.fromisoformat(
                    valid_upto.replace("Z", "+00:00")
                ).date()
            else:
                expiry_date = valid_upto.date()

            today = datetime.now().date()


            if today > expiry_date:


                QMessageBox.critical(
                    parent,
                    "License Expired",
                    "Software license has expired.\nPlease contact Shivvilon Solution."
                )

                return False

            return True

        except Exception as e:
            return False