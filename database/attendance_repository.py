from database.mongodb_connection import MongoDBConnection
from datetime import datetime
from bson import ObjectId 
from utils.db_executor import DBExecutor 
import logging

class AttendanceRepository:
    def __init__(self):
        self.db = MongoDBConnection()
        self.attendance = self.db.attendance
        self.executor = DBExecutor()

    def mark_attendance(self,organization_id,patient_id,serial_no,patient_name,mobile,gender,attendance_date,check_in_time,department,age,problem,payment_per_day,paid_days,used_days):
        record = {
            "organization_id": organization_id,
            "patient_id": patient_id,
            "serial_no": serial_no,
            "patient_name": patient_name,
            "mobile": mobile,
            "gender": gender,
            "check_in_time": check_in_time,
            "department": department,
            "age": age,
            "problem": problem,
            "payment_per_day": payment_per_day,
            "paid_days": paid_days,
            "used_days": used_days,
            "status": "Present",
            "E": None,
            "P": None,
            "attendance_date": attendance_date,
            "created_at": datetime.now(),
        }
        return self.executor.execute("INSERT", "attendance", record)
    
    def update_action_status(self, attendance_id, field_name, value):
        self.attendance.update_one(
            {"_id": attendance_id},
            {
                "$set": {
                    field_name: value
                }
            }
        )

    def is_attendance_taken_today(self, organization_id, patient_id, attendance_date):
        return self.attendance.find_one({
            "organization_id": organization_id,
            "patient_id": patient_id,
            "attendance_date": attendance_date
        })

    def get_today_logs(self, organization_id, attendance_date, search_text=None):
        query = {
            "organization_id": organization_id,
            "attendance_date": attendance_date
        }
        
        if search_text:
            query["$or"] = [
                {"patient_name": {"$regex": search_text, "$options": "i"}},
                {"mobile": {"$regex": search_text, "$options": "i"}},
                {"problem": {"$regex": search_text, "$options": "i"}}
            ]
        return list(self.attendance.find(query).sort("created_at", +1))
    
    def update_attendance_details(self, patient_id, name, mobile, age,add_paid_days, department, problem):
        today_date = datetime.now().strftime("%Y-%m-%d")
        try:
            update1 = {"$set": {
                    "patient_name": name,
                    "mobile": mobile,
                    "age": age,
                    "department": department,
                    "paid_days": add_paid_days
            }}
            self.executor.execute("UPDATE", "attendance", {"patient_id": str(patient_id)}, update1)

            update2 = {"$set": {
                    "problem": problem,
            }}
            self.executor.execute("UPDATE", "attendance", {"patient_id": str(patient_id), "attendance_date": {"$gte": today_date}}, update2)

        except Exception as error:
            print(f"Attendance log update error: {error}")

    def count_today_attendance(self, organization_id, attendance_date):
        try:
            return self.attendance.count_documents({
                "organization_id": organization_id,
                "attendance_date": attendance_date
            })
        except Exception:
            return 0
        

    def get_patient_attendance_history(self, organization_id, patient_id):
        query = {
            "organization_id": organization_id,
            "patient_id": patient_id
        }

        return list(
            self.attendance.find(
                query,
                {
                    "_id": 0,
                    "patient_name": 1,
                    "attendance_date": 1,
                    "check_in_time": 1,
                    "paid_days": 1,       
                    "used_days": 1        
                }
            ).sort("attendance_date", -1)
        )

    def get_department_attendance_count(self, organization_id, attendance_date, department):
        try:
            return self.attendance.count_documents({
                "organization_id": organization_id,
                "attendance_date": attendance_date,
                "department": department
            })
        except Exception:
            return 0
        
    def delete_attendance(self, attendance_id):
        try:
            self.executor.execute(
                "DELETE", 
                "attendance", 
                {"_id": ObjectId(attendance_id)}
            )
            return True
        except Exception as error:
            print(f"Error deleting attendance: {error}")
            return False
    
    def get_patient_attendance_count(self, organization_id, patient_id):
        try:
            return self.attendance.count_documents({
                "organization_id": organization_id,
                "patient_id": patient_id,
                "used_days": {"$gt": 0}  
            })
        except Exception as error:
            logging.error(
                f"Get Patient Attendance Count Error | "
                f"Error: {error}",
                exc_info=True
            )
            return 0
        

    # def upgrade_consulting_to_treatment(self, patient_id):
    #     today_date = datetime.now().strftime("%Y-%m-%d")
    #     try:
    #         record = self.attendance.find_one({
    #             "patient_id": str(patient_id),
    #             "attendance_date": today_date,
    #             "used_days": 0
    #         })
    #         if record:
    #             organization_id = record["organization_id"]
    #             attendance_count = self.get_patient_attendance_count(organization_id, str(patient_id))
                
    #             self.attendance.update_one(
    #                 {"_id": record["_id"]},
    #                 {"$set": {"used_days": attendance_count + 1}}
    #             )
    #     except Exception as error:
    #         print(f"Upgrade consulting error: {error}")

    def upgrade_consulting_to_treatment(
        self,
        patient_id,
        payment_per_day,
        paid_days,
    ):
        today_date = datetime.now().strftime("%Y-%m-%d")

        try:
            record = self.attendance.find_one({
                "patient_id": str(patient_id),
                "attendance_date": today_date,
                "used_days": 0
            })

            if not record:
                return

            organization_id = record["organization_id"]

            attendance_count = self.get_patient_attendance_count(
                organization_id,
                str(patient_id)
            )
            print(attendance_count)
            self.attendance.update_one(
                {"_id": record["_id"]},
                {
                    "$set": {
                        "used_days": attendance_count + 1,
                        "payment_per_day": payment_per_day,
                        "paid_days": paid_days,
                    }
                }
            )

        except Exception as error:
            print(f"Upgrade consulting error: {error}")

    def get_attendance_by_patient_id(self, patient_id):
        try:
            attendance = self.attendance.find_one({"patient_id": str(patient_id)})
            if attendance:
                return attendance
            else:
                return []
        except Exception as error:
            logging.error(f"Get Attendance Error: {error}", exc_info=True)
            return []

    def downgrade_treatment_to_consulting(self, patient_id, payment_per_day, paid_days):
        today_date = datetime.now().strftime("%Y-%m-%d")

        self.attendance.update_one(
            {
                "patient_id": str(patient_id),
                "attendance_date": today_date
            },
            {
                "$set": {
                    "used_days": 0,
                    "payment_per_day": payment_per_day,
                        "paid_days": paid_days,
                }
            }
        )