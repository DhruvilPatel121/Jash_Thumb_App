from os import strerror

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
            logging.error(f"Update Attendance Details Error: {error}", exc_info=True)

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
        
    # def delete_attendance(self, attendance_id):
    #     try:
    #         self.executor.execute(
    #             "DELETE", 
    #             "attendance", 
    #             {"_id": ObjectId(attendance_id)}
    #         )
    #         return True
    #     except Exception as error:
    #         print(f"Error deleting attendance: {error}")
    #         return False

    def update_attendance_logs(self, attendance_id, organization_id, patient_id, attendance_date):
        """
        Update attendance logs after deletion with rollback capability.
        Decrements used_days by 1 for all future attendance logs where used_days > 0.
        Tracks all updates for rollback if any operation fails.
        
        Args:
            attendance_id: ID of the attendance record to be deleted
            organization_id: Organization ID
            patient_id: Patient ID
            attendance_date: Attendance date of the record to be deleted
            
        Returns:
            tuple: (bool: success, list: updated_record_ids for rollback)
        """
        updated_records = []
        
        try:
            # Get all future attendance logs (after the deletion date) where used_days > 0
            future_attendances = list(self.attendance.find({
                "organization_id": organization_id,
                "patient_id": str(patient_id),
                "attendance_date": {"$gt": attendance_date},
                "used_days": {"$gt": 0}
            }).sort("attendance_date", 1))
            
            if not future_attendances:
                return True, []
            
            # Update each future attendance log by decrementing used_days by 1
            for future_record in future_attendances:
                record_id = future_record["_id"]
                try:
                    # Use executor for consistent sync to Atlas
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
                        # Update failed for this record
                        logging.warning(
                            f"Failed to update record {record_id} | "
                            f"Patient ID: {patient_id}"
                        )
                        # Rollback all previous updates
                        self._rollback_attendance_updates(updated_records)
                        return False, []
                        
                except Exception as e:
                    logging.error(
                        f"Error updating record {record_id} | "
                        f"Error: {e}",
                        exc_info=True
                    )
                    # Rollback all previous updates
                    self._rollback_attendance_updates(updated_records)
                    return False, []
            
            return True, updated_records
            
        except Exception as error:
            logging.error(
                f"Error fetching future attendance logs | "
                f"Patient ID: {patient_id}, Date: {attendance_date} | "
                f"Error: {error}",
                exc_info=True
            )
            # Rollback any updates that were made
            if updated_records:
                self._rollback_attendance_updates(updated_records)
            return False, []

    def _rollback_attendance_updates(self, record_ids):
        """
        Rollback all updated records by incrementing used_days back by 1.
        Uses executor for consistent sync to Atlas.
        
        Args:
            record_ids: List of record IDs to rollback
        """
        try:
            for record_id in record_ids:
                rollback_query = {"$inc": {"used_days": 1}}
                self.executor.execute(
                    "UPDATE",
                    "attendance",
                    {"_id": record_id},
                    rollback_query
                )
            logging.info(f"Rollback completed for {len(record_ids)} records")
        except Exception as error:
            logging.error(
                f"Critical Error: Rollback failed! | "
                f"Records affected: {record_ids} | "
                f"Error: {error}",
                exc_info=True
            )

    def delete_attendance(self, attendance_id):
        """
        Delete an attendance record and update future attendance logs accordingly.
        Implements complete rollback if any operation fails.
        Uses executor for consistent sync to both Compass and Atlas.
        
        Args:
            attendance_id: ID of the attendance record to delete
            
        Returns:
            bool: True if deletion successful, False otherwise
        """
        try:
            # 1. Get attendance details before deleting
            attendance = self.attendance.find_one(
                {"_id": ObjectId(attendance_id)}
            )
            
            if not attendance:
                print(f"Attendance record not found: {attendance_id}")
                return False
            
            organization_id = attendance.get("organization_id")
            patient_id = attendance.get("patient_id")
            attendance_date = attendance.get("attendance_date")
            used_days = attendance.get("used_days", 0)
            
            print(f"Attendance details before deletion: {attendance}")
            
            updated_records = []
            
            # 2. Update future attendance logs only if used_days > 0
            if used_days > 0:
                update_success, updated_records = self.update_attendance_logs(
                    attendance_id,
                    organization_id,
                    patient_id,
                    attendance_date
                )
                
                if not update_success:
                    print(f"Failed to update attendance logs for attendance_id: {attendance_id}")
                    # Rollback already handled in update_attendance_logs
                    return False
            
            # 3. Delete attendance using executor for Atlas sync
            delete_result = self.executor.execute(
                "DELETE",
                "attendance",
                {"_id": ObjectId(attendance_id)}
            )
            
            if not delete_result:
                print(f"Failed to delete attendance record: {attendance_id}")
                # Rollback the log updates since deletion failed
                if updated_records:
                    self._rollback_attendance_updates(updated_records)
                return False
            
            print(f"Successfully deleted attendance record: {attendance_id}")
            return True
            
        except Exception as error:
            print(f"Error deleting attendance: {str(error)}")
            logging.error(
                f"Delete Attendance Error | "
                f"Attendance ID: {attendance_id} | "
                f"Error: {error}",
                exc_info=True
            )
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
            print(f"Upgrade consulting error: {error}")

    def get_attendance_by_patient_id(self, patient_id):
        try:
            attendance = self.attendance.find_one({"patient_id": str(patient_id) ,"attendance_date": datetime.now().strftime("%Y-%m-%d")})
            if attendance:
                return attendance
            else:
                return []
        except Exception as error:
            logging.error(f"Get Attendance Error: {error}", exc_info=True)
            return []

    def downgrade_treatment_to_consulting(self, patient_id, payment_per_day, paid_days):
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