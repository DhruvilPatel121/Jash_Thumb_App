from database.mongodb_connection import MongoDBConnection
from datetime import datetime


class AttendanceRepository:
    def __init__(self):
        self.db = MongoDBConnection()
        self.attendance = self.db.attendance

    def mark_attendance(self, organization_id, patient_id,serial_no, patient_name, mobile, attendance_date, check_in_time, department, age, problem):
        record = {
            "organization_id": organization_id,
            "patient_id": patient_id,
            "serial_no":serial_no,
            "patient_name": patient_name,
            "mobile": mobile,
            "attendance_date": attendance_date,
            "check_in_time": check_in_time,
            "department": department,
            "age": age,
            "problem": problem,
            "status": "Present",
            "created_at": datetime.now()
        }
        return self.attendance.insert_one(record).inserted_id

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
            
        return list(self.attendance.find(query).sort("created_at", -1))

    def count_today_attendance(self, organization_id, attendance_date):
        try:
            return self.attendance.count_documents({
                "organization_id": organization_id,
                "attendance_date": attendance_date
            })
        except Exception:
            return 0