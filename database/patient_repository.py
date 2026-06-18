from database.mongodb_connection import MongoDBConnection, check_connection
from datetime import datetime
import logging

class PatientRepository:
    def __init__(self):
        self.db = MongoDBConnection()
        self.patients = (self.db.patients)
        self.deleted_patients = (self.db.deleted_patients)

    @check_connection
    def create_patient(
        self,
        organization_id,
        name,
        email,
        mobile,
        age,
        gender,
        department,
        problem,
        fingerprint_template
    ):
        serial_no = (
            self.patients.count_documents({"organization_id": organization_id}) + 1
        )
        try:
            patient = {
                "organization_id": organization_id,
                "serial_no": serial_no,
                "name": name,
                "email": email,
                "mobile": mobile,
                "age": age,
                "gender": gender,
                "department": department,
                "problem": problem,
                "fingerprint_template": fingerprint_template,
                "created_at": datetime.now(),
            }
            return self.patients.insert_one(patient).inserted_id
        except Exception as error:
            logging.error(f"Create Patient Error: {error}", exc_info=True)
            return None

    def get_all_by_organization(self, organization_id, search_text=None):
        try:
            query = {"organization_id": organization_id}
            if search_text:
                query["$or"] = [
                    {"name": {"$regex": search_text, "$options": "i"}},
                    {"mobile": {"$regex": search_text, "$options": "i"}},
                    {"problem": {"$regex": search_text, "$options": "i"}},
                ]
            return list(self.patients.find(query))
        except Exception as error:
            logging.error(f"Patient fatch from database Error: {error}",exc_info=True)
            return []

    def count_patients(self, organization_id):
        try:
            return self.patients.count_documents({"organization_id": organization_id})
        except Exception:
            return 0

    @check_connection
    def is_mobile_registered(self, mobile):
        try:
            return bool(self.patients.find_one({"mobile": mobile}))
        except Exception as e:
            logging.exception("Mobile Check Error")
            return False

    @check_connection
    def update_patient(
        self,
        patient_id,
        name,
        mobile,
        age,
        gender,
        department,
        problem,
        fingerprint_template=None
    ):
        try:
            update_data = {
                "name": name,
                "mobile": mobile,
                "age": age,
                "gender": gender,
                "department": department,
                "problem": problem,
            }
            if fingerprint_template:
                update_data["fingerprint_template"] = fingerprint_template
            return (
                self.patients.update_one(
                    {"_id": patient_id}, {"$set": update_data}
                ).modified_count
                > 0
            )
        except Exception as error:
            logging.error(f"Update Patient Error | Patient ID: {patient_id} | Error: {error}", exc_info=True)
            return False

    @check_connection
    def delete_patient(self, patient_id):
        try:
            patient = self.patients.find_one({"_id": patient_id})
            if not patient:
                return False
            self.deleted_patients.insert_one(patient)
            result = self.patients.delete_one({"_id": patient_id})
            self.patients.update_many(
                {
                    "organization_id": patient["organization_id"],
                    "serial_no": {"$gt": patient["serial_no"]},
                },
                {"$inc": {"serial_no": -1}},
            )
            return result.deleted_count > 0
        except Exception as error:
            logging.error(f"Delete Patient Error: {error}", exc_info=True)
            return False