from PyQt6.QtCore import QThread, pyqtSignal
from utils.scanner_manager import ScannerManager
from utils.enrollment import Enrollment
from utils.verification import Verification
from database.patient_repository import PatientRepository
from database.attendance_repository import AttendanceRepository
from utils.session import Session
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class AttendanceWorker(QThread):
    scanner_connected = pyqtSignal()
    scanner_connection_failed = pyqtSignal(str)
    scanner_disconnected = pyqtSignal()
    waiting_for_finger = pyqtSignal()
    attendance_marked = pyqtSignal(dict)
    already_taken = pyqtSignal(str)
    patient_not_found = pyqtSignal()

    def __init__(self):
        super().__init__()
        logger.info("Initializing AttendanceWorker")
        self.running = False
        self.processing = False
        self.finger_locked = False
        self.scanner = ScannerManager()
        self.enrollment = Enrollment(self.scanner)
        self.verification = Verification(self.scanner)
        self.patient_repository = PatientRepository()
        self.attendance_repository = AttendanceRepository()
        self.cached_patients = []

    def start_attendance(self):
        logger.info("Starting attendance worker")
        self.organization_id = Session.organization_id
        self.cached_patients = self.patient_repository.get_all_by_organization(self.organization_id)
        self.running = True
        self.start()

    def stop_attendance(self):
        logger.info("Stopping attendance worker")
        self.running = False
        self.wait()
        self.cached_patients = []

    def open_scanner(self):
        logger.info("Opening scanner for attendance")
        if not self.scanner.load_sdk():
            logger.error("Scanner SDK Load Failed")
            return False

        if not self.scanner.create():
            logger.error("Scanner Create Failed")
            return False

        if not self.scanner.initialize():
            logger.error("Scanner Initialize Failed")
            return False

        self.scanner.sdk.SGFPM_SetTemplateFormat(self.scanner.hfpm, 0x0200)

        if not self.scanner.open_device():
            self.scanner_connection_failed.emit("Scanner Not Connected")
            logger.error("Scanner Not Connected")
            return False

        self.scanner.sdk.SGFPM_EnableSmartCapture(self.scanner.hfpm, True)
        self.scanner_connected.emit()
        logger.info("Scanner opened and ready")
        return True

    def close_scanner(self):
        logger.info("Closing attendance scanner")
        try:
            self.scanner.close_device()
            self.scanner.terminate()
            self.scanner_disconnected.emit()
        except Exception as error:
            logger.error("Scanner Close Error", exc_info=True)

    def process_attendance(self, image):
        logger.info("Processing attendance image")
        try:
            template = self.enrollment.create_template_bytes(image)
            if not template:
                logger.warning("Attendance template creation failed")
                return

            patient = self.verification.identify_patient_attendance(template, self.cached_patients)
            if not patient:
                self.patient_not_found.emit()
                logger.warning("No matching patient found for attendance")
                return

            fresh_patient = self.patient_repository.patients.find_one({"_id": patient["_id"]})
            if fresh_patient:
                patient = fresh_patient

            current_time = datetime.now().strftime("%H:%M:%S")
            today_date = datetime.now().strftime("%Y-%m-%d")
            attendance = self.attendance_repository.is_attendance_taken_today(
                self.organization_id, str(patient["_id"]), today_date
            )
            if attendance:
                self.already_taken.emit(patient["name"])
                logger.info("Attendance already taken today for %s", patient["name"])
                return

            department = patient.get("department", "").strip()
            if not department or department.lower() not in ["ortho", "neuro"]:
                department = "Ortho"
            patient["department"] = department

            attendance_count = self.attendance_repository.get_patient_attendance_count(
                self.organization_id, str(patient["_id"])
            )

            created_at = patient.get("created_at")
            is_registration_day = False
            if created_at:
                reg_date = created_at.strftime("%Y-%m-%d") if isinstance(created_at, datetime) else str(created_at)[:10]
                if reg_date == today_date:
                    is_registration_day = True
            elif attendance_count == 0:
                is_registration_day = True

            treatment_start_today = bool(patient.get("treatment_start_from_today", False))

            if not treatment_start_today:
                used_days = 0
                payment_per_day = 0
                paid_days = 0
            else:
                payment_per_day = patient.get("payment_per_day", 0)
                paid_days = patient.get("paid_days", 0)

                if attendance_count == 0:
                    used_days = 1
                else:
                    used_days = attendance_count + 1

            self.attendance_repository.mark_attendance(
                self.organization_id,
                str(patient["_id"]),
                patient.get("token_no", ""),
                patient.get("name", ""),
                patient.get("mobile", ""),
                patient.get("gender", ""),
                today_date,
                current_time,
                department,
                patient.get("age", ""),
                patient.get("problem", ""),
                payment_per_day,
                paid_days,
                used_days,
            )

            patient["attendance_time"] = current_time
            token_no = self.attendance_repository.get_department_attendance_count(
                self.organization_id, today_date, department
            )
            patient["token_no"] = token_no
            patient["display_department"] = department

            self.attendance_marked.emit(patient)
            logger.info("Attendance marked for patient %s", patient.get("name", "Unknown"))
        finally:
            self.processing = False
            logger.debug("Finished processing attendance image")

    def run(self):
        logger.info("AttendanceWorker thread started")
        scanner_ready = self.open_scanner()
        if not scanner_ready:
            self.running = False
            logger.warning("Scanner not ready, stopping AttendanceWorker")
            return
        while self.running:
            try:
                QThread.msleep(300)
                if self.processing:
                    QThread.msleep(100)
                    continue
                self.waiting_for_finger.emit()
                image, _ = self.scanner.capture_image_attend()
                if not image:
                    self.finger_locked = False
                    QThread.msleep(1000)
                    continue
                if self.finger_locked:
                    QThread.msleep(1000)
                    continue
                self.finger_locked = True
                self.processing = True
                self.process_attendance(image)
            except Exception as error:
                logger.error("Attendance Error", exc_info=True)
                self.processing = False
                self.finger_locked = False
                continue
        self.close_scanner()

    def process_manual_attendance(self, patient):
        logger.info("Processing manual attendance for patient %s", patient.get("_id"))
        try:
            self.processing = True
            self.organization_id = Session.organization_id

            fresh_patient = self.patient_repository.patients.find_one({"_id": patient["_id"]})
            if fresh_patient:
                patient = fresh_patient

            current_time = datetime.now().strftime("%H:%M:%S")
            today_date = datetime.now().strftime("%Y-%m-%d")

            attendance = self.attendance_repository.is_attendance_taken_today(
                self.organization_id, str(patient["_id"]), today_date
            )
            if attendance:
                self.already_taken.emit(patient["name"])
                logger.info("Manual attendance already taken today for %s", patient["name"])
                return

            department = patient.get("department", "").strip()
            if not department or department.lower() not in ["ortho", "neuro"]:
                department = "Ortho"
            patient["department"] = department

            attendance_count = self.attendance_repository.get_patient_attendance_count(
                self.organization_id, str(patient["_id"])
            )

            created_at = patient.get("created_at")
            is_registration_day = False
            if created_at:
                reg_date = created_at.strftime("%Y-%m-%d") if isinstance(created_at, datetime) else str(created_at)[:10]
                if reg_date == today_date:
                    is_registration_day = True
            elif attendance_count == 0:
                is_registration_day = True

            treatment_start_today = bool(patient.get("treatment_start_from_today", False))

            if not treatment_start_today:
                used_days = 0
                payment_per_day = 0
                paid_days = 0
            else:
                payment_per_day = patient.get("payment_per_day", 0)
                paid_days = patient.get("paid_days", 0)

                if attendance_count == 0:
                    used_days = 1
                else:
                    used_days = attendance_count + 1

            self.attendance_repository.mark_attendance(
                organization_id=self.organization_id,
                patient_id=str(patient["_id"]),
                serial_no=patient.get("token_no", ""),
                patient_name=patient.get("name", ""),
                mobile=patient.get("mobile", ""),
                gender=patient.get("gender", ""),
                attendance_date=today_date,
                check_in_time=current_time,
                department=department,
                age=patient.get("age", ""),
                problem=patient.get("problem", ""),
                payment_per_day=payment_per_day,
                paid_days=paid_days,
                used_days=used_days,
            )

            patient["attendance_time"] = current_time
            token_no = self.attendance_repository.get_department_attendance_count(
                self.organization_id, today_date, department
            )
            patient["token_no"] = token_no
            patient["display_department"] = department

            self.attendance_marked.emit(patient)
            logger.info("Manual attendance marked for patient %s", patient.get("name", "Unknown"))
        except Exception as error:
            logger.error("Manual Attendance Error", exc_info=True)
        finally:
            self.processing = False