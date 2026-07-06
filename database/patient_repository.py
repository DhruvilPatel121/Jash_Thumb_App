from bson import ObjectId
from database.mongodb_connection import MongoDBConnection, check_connection
from datetime import datetime, timedelta
import logging
from utils.db_executor import DBExecutor

logger = logging.getLogger(__name__)

class PatientRepository:
    def __init__(self):
        logger.info("Initializing PatientRepository")
        self.db = MongoDBConnection()
        self.patients = self.db.patients
        self.deleted_patients = self.db.deleted_patients
        self.executor = DBExecutor()

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
        consultancy_fees,
        payment_per_day,
        paid_days,
        # only_consulting,
        fingerprint_template
    ):
        logger.info("Creating patient record")
        logger.debug(
            "Patient create payload organization_id=%s name=%s mobile=%s age=%s gender=%s department=%s",
            organization_id,
            name,
            mobile,
            age,
            gender,
            department,
        )
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
                "consultancy_fees": consultancy_fees,
                "payment_per_day": payment_per_day,
                "paid_days": paid_days,
                # "only_consulting": only_consulting,
                "treatment_start_from_today": False,
                "fingerprint_template": fingerprint_template,
                "created_at": datetime.now()
            }
            return self.executor.execute("INSERT", "patients", patient)
        except Exception as error:
            logger.error(f"Create Patient Error: {error}", exc_info=True)
            return None

    def get_all_by_organization(self, organization_id):
        logger.info("Fetching all patients for organization_id=%s", organization_id)
        try:
            query = {"organization_id": organization_id}
            return list(self.patients.find(query))
        except Exception as error:
            logger.error(f"Patient fetch from database Error: {error}", exc_info=True)
            return []

    def get_patient_data(self, organization_id, selected_date=None, search_text=None):
        logger.info(
            "Fetching patient data organization_id=%s selected_date=%s search_text=%s",
            organization_id,
            selected_date,
            search_text,
        )
        try:
            query = {"organization_id": organization_id}

            if selected_date:
                start_date = datetime.strptime(selected_date, "%Y-%m-%d")
                end_date = start_date + timedelta(days=1)

                query["created_at"] = {
                    "$gte": start_date,
                    "$lt": end_date
                }

            if search_text:
                query["$or"] = [
                    {"name": {"$regex": search_text, "$options": "i"}},
                    {"mobile": {"$regex": search_text, "$options": "i"}},
                    {"problem": {"$regex": search_text, "$options": "i"}},
                ]

            return list(self.patients.find(query))

        except Exception as error:
            logger.error(f"Patient fetch from database Error: {error}", exc_info=True)
            return []

    def count_patients(self, organization_id):
        logger.info("Counting patients for organization_id=%s", organization_id)
        try:
            return self.patients.count_documents({"organization_id": organization_id})
        except Exception as error:
            logger.error(f"Count patients error: {error}", exc_info=True)
            return 0

    @check_connection
    def update_patient(
        self,
        patient_id,
        name,
        mobile,
        age,
        gender,
        department,
        consultancy_fees,
        payment_per_day,
        add_paid_days,
        problem,
        fingerprint_template=None,
        treatment_start_from_today=False
    ):
        logger.info("Updating patient record %s", patient_id)
        logger.debug(
            "Update patient payload name=%s mobile=%s age=%s gender=%s department=%s",
            name,
            mobile,
            age,
            gender,
            department,
        )
        try:
            update_data = {
                "name": name,
                "mobile": mobile,
                "age": age,
                "gender": gender,
                "department": department,
                "consultancy_fees": consultancy_fees,
                "payment_per_day": payment_per_day,
                "paid_days": add_paid_days,
                "problem": problem,
                # "only_consulting": not treatment_start_from_today,
                "treatment_start_from_today": treatment_start_from_today
            }
            if fingerprint_template is not None:
                update_data["fingerprint_template"] = fingerprint_template

            return self.executor.execute(
                "UPDATE", "patients",
                {"_id": patient_id},
                {"$set": update_data}
            )
        except Exception as error:
            logger.error(f"Update Patient Error | Patient ID: {patient_id} | Error: {error}", exc_info=True)
            return False

    @check_connection
    def delete_patient(self, patient_id):
        logger.info("Deleting patient record %s", patient_id)
        try:
            patient = self.patients.find_one({"_id": patient_id})
            if not patient:
                logger.warning("Patient record not found for delete: %s", patient_id)
                return False

            self.deleted_patients.insert_one(patient)
            result = self.executor.execute("DELETE", "patients", {"_id": patient_id})

            self.patients.update_many(
                {
                    "organization_id": patient["organization_id"],
                    "serial_no": {"$gt": patient["serial_no"]},
                },
                {"$inc": {"serial_no": -1}},
            )
            return result
        except Exception as error:
            logger.error(f"Delete Patient Error: {error}", exc_info=True)
            return False