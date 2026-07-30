from os import strerror

from database.mongodb_connection import MongoDBConnection
from datetime import datetime
from bson import ObjectId 
from utils.db_executor import DBExecutor 
import logging

logger = logging.getLogger(__name__)

class AttendanceRepository:
    def __init__(self):
        logger.info("Initializing AttendanceRepository")
        self.db = MongoDBConnection()
        self.attendance = self.db.attendance
        self.executor = DBExecutor()

    def mark_attendance(self,organization_id,patient_id,serial_no,patient_name,mobile,gender,attendance_date,check_in_time,department,age,problem,payment_per_day,paid_days,used_days):
        logger.info("Marking attendance for patient_id=%s attendance_date=%s", patient_id, attendance_date)
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
        logger.info("Updating attendance action status for attendance_id=%s field_name=%s", attendance_id, field_name)
        update_query = {
            "$set": {
                field_name: value
            }
        }
        self.executor.execute(
            "UPDATE",
            "attendance",
            {"_id": attendance_id},
            update_query
        )

    def is_attendance_taken_today(self, organization_id, patient_id, attendance_date):
        logger.info("Checking attendance taken today organization_id=%s patient_id=%s date=%s", organization_id, patient_id, attendance_date)
        return self.attendance.find_one({
            "organization_id": organization_id,
            "patient_id": patient_id,
            "attendance_date": attendance_date
        })

    def get_today_logs(self, organization_id, attendance_date, search_text=None):
        logger.info("Fetching today attendance logs for organization_id=%s date=%s search_text=%s", organization_id, attendance_date, search_text)
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
        logger.info("Updating attendance details for patient_id=%s", patient_id)
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
            logger.error("Attendance log update error", exc_info=True)

    def count_today_attendance(self, organization_id, attendance_date):
        logger.info("Counting today attendance for organization_id=%s attendance_date=%s", organization_id, attendance_date)
        try:
            return self.attendance.count_documents({
                "organization_id": organization_id,
                "attendance_date": attendance_date
            })
        except Exception as error:
            logger.error("Count today attendance error", exc_info=True)
            return 0
        

    def get_patient_attendance_history(self, organization_id, patient_id):
        logger.info("Fetching attendance history for patient_id=%s", patient_id)
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
        logger.info("Getting department attendance count organization_id=%s attendance_date=%s department=%s", organization_id, attendance_date, department)
        try:
            return self.attendance.count_documents({
                "organization_id": organization_id,
                "attendance_date": attendance_date,
                "department": department
            })
        except Exception as error:
            logger.error("Get department attendance count error", exc_info=True)
            return 0
        
    def update_attendance_logs(self, attendance_id, organization_id, patient_id, attendance_date):
        logger.info("Updating future attendance logs for patient_id=%s attendance_date=%s", patient_id, attendance_date)
        updated_records = []
        
        try:
            future_attendances = list(self.attendance.find({
                "organization_id": organization_id,
                "patient_id": str(patient_id),
                "attendance_date": {"$gt": attendance_date},
                "used_days": {"$gt": 0}
            }).sort("attendance_date", 1))
            
            if not future_attendances:
                logger.debug("No future attendance logs found to update")
                return True, []
            
            for future_record in future_attendances:
                record_id = future_record["_id"]
                try:
                    update_query = {"$inc": {"used_days": -1}}
                    result = self.executor.execute(
                        "UPDATE",
                        "attendance",
                        {"_id": record_id},
                        update_query
                    )
                    
                    if result:
                        updated_records.append(record_id)
                    else:
                        logger.warning("Failed to update record %s while updating future attendance logs", record_id)
                        self._rollback_attendance_updates(updated_records)
                        return False, []
                        
                except Exception as e:
                    logger.error("Error updating record %s during future attendance logs update", record_id, exc_info=True)
                    self._rollback_attendance_updates(updated_records)
                    return False, []
            
            return True, updated_records
            
        except Exception as error:
            logger.error(
                "Error fetching future attendance logs",
                exc_info=True
            )
            if updated_records:
                self._rollback_attendance_updates(updated_records)
            return False, []

    def _rollback_attendance_updates(self, record_ids):
        logger.info("Rolling back attendance updates for %s records", len(record_ids))
        try:
            for record_id in record_ids:
                rollback_query = {"$inc": {"used_days": 1}}
                self.executor.execute(
                    "UPDATE",
                    "attendance",
                    {"_id": record_id},
                    rollback_query
                )
            logger.info("Rollback completed for %s records", len(record_ids))
        except Exception as error:
            logger.error(
                "Critical Error: Rollback failed",
                exc_info=True
            )

    def delete_attendance(self, attendance_id):
        logger.info("Deleting attendance record %s", attendance_id)
        try:
            attendance = self.attendance.find_one(
                {"_id": ObjectId(attendance_id)}
            )
            
            if not attendance:
                logger.warning("Attendance record not found for deletion: %s", attendance_id)
                return False
            
            organization_id = attendance.get("organization_id")
            patient_id = attendance.get("patient_id")
            attendance_date = attendance.get("attendance_date")
            used_days = attendance.get("used_days", 0)
            
            updated_records = []
            
            if used_days > 0:
                update_success, updated_records = self.update_attendance_logs(
                    attendance_id,
                    organization_id,
                    patient_id,
                    attendance_date
                )
                
                if not update_success:
                    logger.warning("Failed to update attendance logs before deletion for attendance_id=%s", attendance_id)
                    return False
            
            delete_result = self.executor.execute(
                "DELETE",
                "attendance",
                {"_id": ObjectId(attendance_id)}
            )
            
            if not delete_result:
                logger.warning("Failed to delete attendance record %s", attendance_id)
                if updated_records:
                    self._rollback_attendance_updates(updated_records)
                return False
            
            logger.info("Attendance record deleted successfully %s", attendance_id)
            return True
            
        except Exception as error:
            logger.error(
                "Delete Attendance Error",
                exc_info=True
            )
            return False

    def get_patient_attendance_count(self, organization_id, patient_id):
        logger.info("Getting patient attendance count organization_id=%s patient_id=%s", organization_id, patient_id)
        try:
            return self.attendance.count_documents({
                "organization_id": organization_id,
                "patient_id": patient_id,
                "used_days": {"$gt": 0}  
            })
        except Exception as error:
            logger.error(
                "Get Patient Attendance Count Error",
                exc_info=True
            )
            return 0
        

    def upgrade_consulting_to_treatment(
        self,
        patient_id,
        payment_per_day,
        paid_days,
    ):
        logger.info("Upgrading consulting to treatment for patient_id=%s", patient_id)
        today_date = datetime.now().strftime("%Y-%m-%d")

        try:
            record = self.attendance.find_one({
                "patient_id": str(patient_id),
                "attendance_date": today_date,
                "used_days": 0
            })

            if not record:
                logger.debug("No attendance record found to upgrade for patient_id=%s", patient_id)
                return

            organization_id = record["organization_id"]

            attendance_count = self.get_patient_attendance_count(
                organization_id,
                str(patient_id)
            )
            
            update_query = {
                "$set": {
                    "used_days": attendance_count + 1,
                    "payment_per_day": payment_per_day,
                    "paid_days": paid_days,
                }
            }
            self.executor.execute(
                "UPDATE",
                "attendance",
                {"_id": record["_id"]},
                update_query
            )

        except Exception as error:
            logger.error("Upgrade consulting error", exc_info=True)

    def get_attendance_by_patient_id(self, patient_id):
        logger.info("Getting attendance by patient_id=%s", patient_id)
        try:
            attendance = self.attendance.find_one({"patient_id": str(patient_id) ,"attendance_date": datetime.now().strftime("%Y-%m-%d")})
            if attendance:
                return attendance
            else:
                return []
        except Exception as error:
            logger.error("Get Attendance Error", exc_info=True)
            return []

    def downgrade_treatment_to_consulting(self, patient_id, payment_per_day, paid_days):
        logger.info("Downgrading treatment to consulting for patient_id=%s", patient_id)
        today_date = datetime.now().strftime("%Y-%m-%d")

        update_query = {
            "$set": {
                "used_days": 0,
                "payment_per_day": payment_per_day,
                "paid_days": paid_days,
            }
        }
        self.executor.execute(
            "UPDATE",
            "attendance",
            {
                "patient_id": str(patient_id),
                "attendance_date": today_date
            },
            update_query
        )

    def get_monthly_payment_status(self, organization_id, month, year):
        logger.info("Getting monthly payment status for org=%s, month=%s, year=%s", organization_id, month, year)
        
        try:
            if isinstance(month, str) and not month.isdigit():
                month_names = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
                month = month_names.index(month) + 1
            else:
                month = int(month)
                
            year = int(year)
            
            start_date = datetime(year, month, 1)
            if month == 12:
                end_date = datetime(year + 1, 1, 1)
            else:
                end_date = datetime(year, month + 1, 1)

            pipeline = [
                {
                    "$match": {
                        "organization_id": organization_id,
                        "created_at": {"$gte": start_date, "$lt": end_date}
                    }
                },
                {
                    "$sort": {"created_at": 1}
                },
                {
                    "$group": {
                        "_id": "$patient_id",
                        "latest_record": {"$last": "$$ROOT"}
                    }
                },
                {
                    "$replaceRoot": {"newRoot": "$latest_record"}
                },
                {
                    "$sort": {"created_at": 1}
                }
            ]

            records = list(self.attendance.aggregate(pipeline))
            
            paid_list = []
            due_list = []
            last_day_list = []
            
            today_str = datetime.now().strftime("%Y-%m-%d")
            
            for record in records:
                # Need to safely parse to int in case they are strings in DB
                try:
                    paid_days = int(record.get("paid_days", 0) or 0)
                except ValueError:
                    paid_days = 0
                try:
                    used_days = int(record.get("used_days", 0) or 0)
                except ValueError:
                    used_days = 0
                
                # Skip consultancy-only patients (paid_days=0 and used_days=0)
                if paid_days == 0 and used_days == 0:
                    continue
                
                if used_days < paid_days:
                    paid_list.append(record)
                elif used_days == paid_days:
                    paid_list.append(record)
                    if record.get("attendance_date") == today_str:
                        last_day_list.append(record)
                else:
                    due_list.append(record)
                    
            return paid_list, last_day_list, due_list

        except Exception as error:
            logger.error("Error in get_monthly_payment_status", exc_info=True)
            return [], [], []

    def get_monthly_attendance_counts(self, organization_id, month, year):
        """
        Count attendance records for the selected month:
        - treatment_visits: records where used_days > 0 (actual treatment days used)
        - paid_visits:      records where paid_days > 0 (visits by patients who have paid)
        Consultancy-only visits (used_days == 0) are excluded from both counts.
        """
        logger.info("Getting monthly attendance counts for org=%s, month=%s, year=%s", organization_id, month, year)
        try:
            if isinstance(month, str) and not month.isdigit():
                month_names = ["January", "February", "March", "April", "May", "June",
                               "July", "August", "September", "October", "November", "December"]
                month = month_names.index(month) + 1
            else:
                month = int(month)
            year = int(year)

            start_date = datetime(year, month, 1)
            end_date = datetime(year + 1, 1, 1) if month == 12 else datetime(year, month + 1, 1)

            pipeline = [
                {
                    "$match": {
                        "organization_id": organization_id,
                        "created_at": {"$gte": start_date, "$lt": end_date}
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "treatment_visits": {
                            "$sum": {
                                "$cond": [{"$gt": ["$used_days", 0]}, 1, 0]
                            }
                        },
                        "paid_visits": {
                            "$sum": {
                                "$cond": [{"$gt": ["$paid_days", 0]}, 1, 0]
                            }
                        }
                    }
                }
            ]

            result = list(self.attendance.aggregate(pipeline))
            if result:
                return result[0].get("treatment_visits", 0), result[0].get("paid_visits", 0)
            return 0, 0

        except Exception as error:
            logger.error("Error in get_monthly_attendance_counts", exc_info=True)
            return 0, 0
