from PyQt6.QtCore import (QThread,pyqtSignal)
from utils.scanner_manager import (ScannerManager)
from utils.enrollment import (Enrollment)
from utils.verification import (Verification)
from database.patient_repository import (PatientRepository)
from database.attendance_repository import (AttendanceRepository)
from utils.session import Session
from datetime import datetime
import logging


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
        self.running = False
        self.processing = False
        self.finger_locked = False
        self.scanner = ScannerManager()
        self.enrollment = Enrollment(self.scanner)
        self.verification = Verification(self.scanner)
        self.patient_repository = (PatientRepository())
        self.attendance_repository = (AttendanceRepository())
        self.cached_patients = []


    def start_attendance(self):
        self.organization_id = Session.organization_id
        self.cached_patients = (
            self.patient_repository
            .get_all_by_organization(self.organization_id))
        self.running = True
        self.start()

    def stop_attendance(self):
        self.running = False
        self.wait()
        self.cached_patients = []

    def open_scanner(self):
        if not self.scanner.load_sdk():
            logging.error("Scanner SDK Load Failed")
            return False

        if not self.scanner.create():
            logging.error("Scanner Create Failed")
            return False

        if not self.scanner.initialize():
            logging.error("Scanner Initialize Failed")
            return False

        self.scanner.sdk.SGFPM_SetTemplateFormat(
            self.scanner.hfpm,
            0x0200
        )

        # return True
        if not self.scanner.open_device():
            self.scanner_connection_failed.emit("Scanner Not Connected")
            logging.error("Scanner Not Connected")
            return False

        result = (self.scanner.sdk.SGFPM_EnableSmartCapture(self.scanner.hfpm,True))
        self.scanner_connected.emit()
        return True
    
    def close_scanner(self):
        try:
            self.scanner.close_device()
            self.scanner.terminate()
            self.scanner_disconnected.emit()
        except Exception as error:
            logging.error(f"Scanner Close Error: {error}",exc_info=True)

    def process_attendance(self,image):
        try:
            template = (self.enrollment.create_template_bytes(image))
            if not template:
                return
            patient = (self.verification.identify_patient_attendance(template,self.cached_patients))
            if not patient:
                self.patient_not_found.emit()
                return
            current_time = datetime.now().strftime("%H:%M:%S")
            today_date = datetime.now().strftime("%Y-%m-%d")
            attendance = (self.attendance_repository.is_attendance_taken_today(self.organization_id,str(patient["_id"]),today_date))
            if attendance:
                self.already_taken.emit(
                    patient["name"])
                return
            self.attendance_repository.mark_attendance(
                    self.organization_id,
                    str(patient["_id"]),
                    patient.get("serial_no", ""),       
                    patient.get("name", ""),        
                    patient.get("mobile", ""),
                    today_date,
                    current_time,
                    patient.get("department", ""), 
                    patient.get("age", ""),       
                    patient.get("problem", "") 
                )
            patient["attendance_time"] = current_time
            self.attendance_marked.emit(patient)

        finally:
            self.processing = False

    def run(self):

        
        scanner_ready = (self.open_scanner())
        if not scanner_ready:
            self.running = False
            return
        while self.running:
            try:
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
                logging.error(f"Attendance Error: {error}",exc_info=True)
                self.processing = False
                self.finger_locked = False

                continue
        self.close_scanner()
