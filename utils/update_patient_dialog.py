from PyQt6.QtWidgets import (QFrame, QLabel, QLineEdit, QPushButton, QVBoxLayout,QHBoxLayout, QFormLayout, QRadioButton, QButtonGroup)
from PyQt6.QtCore import Qt, pyqtSignal,QEvent
from utils.toast_notification import ToastNotification
from database.patient_repository import PatientRepository
from database.mongodb_connection import DatabaseConnectionError
from utils.scanner_manager import ScannerManager
from utils.enrollment import Enrollment
from utils.verification import Verification
from utils.session import Session


class UpdatePatientDialog(QFrame):
    patient_updated = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.patient_repository = PatientRepository()
        self.setup_ui()
        self.scanner = ScannerManager()
        self.enrollment = Enrollment(self.scanner)
        self.verification = Verification(self.scanner)
        self.template_bytes = None

    def setup_ui(self):
        self.setObjectName("updateCard")
        self.hide()
        self.setFixedSize(600, 500)

        # ---------------------------------------------------------
        # MODERN CSS ADDED HERE
        # ---------------------------------------------------------
        self.setStyleSheet("""
        QFrame#updateCard {
            background-color: #ffffff;
            border: 1px solid #cbd5e1;
            border-radius: 12px;
        }
        QLabel {
            background-color: transparent;
            color: #334155;
            font-size: 14px;
            font-weight: bold;
        }
        QLabel#titleLabel {
            background-color: transparent;               
            color: #0f172a;
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 10px;
        }
        QLineEdit {
            background-color: #f8fafc;
            border: 1px solid #cbd5e1;
            border-radius: 6px;
            padding: 8px 12px;
            color: #0f172a;
            font-size: 14px;
            min-height: 20px;
        }
        QLineEdit:focus{
            border: 2px solid #4f46e5;
            background-color: #ffffff;
        }
        QRadioButton {
            color: black;
            font-size: 14px;
            font-weight: 600;
            background: transparent;
            spacing: 8px;
            padding: 4px;
        }
        QRadioButton:focus {
            border: 2px solid #4F46E5;
            border-radius: 6px;
            background-color: #EEF2FF;
        }
        QRadioButton::indicator {
            width: 18px;
            height: 18px;
            border: 2px solid #94A3B8;
            border-radius: 9px;
            background: white;
        }
        QRadioButton::indicator:checked {
            background-color: #4F46E5;
            border: 2px solid #4F46E5;
        }
        QRadioButton::indicator:hover {
            border: 2px solid #6366F1;
        }
        
        /* --- General Button Style --- */
        QPushButton {
            padding: 10px 20px;
            font-size: 14px;
            font-weight: bold;
            border-radius: 6px;
            min-width: 100px;
        }
        
        /* --- Cancel Button (Kept Gray/Neutral) --- */
        QPushButton#cancelBtn {
            background-color: #f1f5f9;
            color: #475569;
            border: 1px solid #cbd5e1;
        }
        QPushButton#cancelBtn:hover {
            background-color: #e2e8f0;
        }

        /* --- Capture & Save Buttons (Your New Style Applied Here) --- */
        QPushButton#captureBtn, QPushButton#saveBtn {
            background-color: #5C62D6;
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 14px;
            font-weight: 600;
        }
        QPushButton#captureBtn:hover, QPushButton#saveBtn:hover {
            background-color: #4C51BF;
        }
        QPushButton#captureBtn:pressed, QPushButton#saveBtn:pressed {
            border: 1px solid #1D4ED8;
            padding-top: 2px;
            padding-left: 2px;
        }
        """)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)
        self.setLayout(main_layout)

        title = QLabel("Update Patient")
        title.setObjectName("titleLabel")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)

        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        main_layout.addLayout(form_layout)

        self.name_input = QLineEdit()
        self.mobile_input = QLineEdit()
        self.age_input = QLineEdit()
        
        # Gender Radio Buttons
        self.gender_layout = QHBoxLayout()
        self.male_radio = QRadioButton("Male")
        self.female_radio = QRadioButton("Female")
        self.gender_group = QButtonGroup()
        self.gender_group.addButton(self.male_radio)
        self.gender_group.addButton(self.female_radio)
        self.gender_layout.addWidget(self.male_radio)
        self.gender_layout.addWidget(self.female_radio)
        self.gender_layout.addStretch()

        # Department Radio Buttons
        self.department_layout = QHBoxLayout()
        self.dep1_radio = QRadioButton("Neurologist")
        self.dep2_radio = QRadioButton("Cardiologist")
        self.department_group = QButtonGroup()
        self.department_group.addButton(self.dep1_radio)
        self.department_group.addButton(self.dep2_radio)
        self.department_layout.addWidget(self.dep1_radio)
        self.department_layout.addWidget(self.dep2_radio)
        self.department_layout.addStretch()
        
        self.problem_input = QLineEdit()
        
        form_layout.addRow("Name", self.name_input)
        form_layout.addRow("Mobile", self.mobile_input)
        form_layout.addRow("Age", self.age_input)
        form_layout.addRow("Gender", self.gender_layout)
        form_layout.addRow("Department", self.department_layout)
        form_layout.addRow("Problem", self.problem_input)
        
        self.capture_btn = QPushButton("Capture")
        self.capture_btn.clicked.connect(self.capture_fingerprint)
        self.capture_btn.setObjectName("captureBtn")
        self.capture_btn.setFixedSize(120, 40)

        self.fingerprint_status = QLabel("")
        self.fingerprint_status.setStyleSheet("""
        QLabel{
            color:#64748B;
            font-size:13px;
            font-weight:600;
            border:none;
        }
        """)

        fingerprint_row = QHBoxLayout()
        fingerprint_row.addWidget(self.capture_btn)
        fingerprint_row.addWidget(self.fingerprint_status)
        fingerprint_row.addStretch()

        form_layout.addRow("Fingerprint", fingerprint_row)

        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 10, 0, 0)
        button_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        main_layout.addLayout(button_layout)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setObjectName("cancelBtn") 
        
        self.save_btn = QPushButton("Save")
        self.save_btn.setObjectName("saveBtn")

        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.save_btn)

        self.cancel_btn.clicked.connect(self.cancel_update)
        self.save_btn.clicked.connect(self.save_updated_patient)

        # Event Filters for Custom Tab Order
        self.age_input.installEventFilter(self)
        self.male_radio.installEventFilter(self)
        self.female_radio.installEventFilter(self)
        self.dep1_radio.installEventFilter(self)
        self.dep2_radio.installEventFilter(self)


    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.KeyPress:
            if event.key() == Qt.Key.Key_Tab:
                if obj == self.age_input:
                    self.male_radio.setFocus()
                    return True
                elif obj == self.male_radio:
                    self.female_radio.setFocus()
                    return True
                elif obj == self.female_radio:
                    self.dep1_radio.setFocus()
                    return True
                elif obj == self.dep1_radio:
                    self.dep2_radio.setFocus()
                    return True
                elif obj == self.dep2_radio:
                    self.problem_input.setFocus()
                    return True

        return super().eventFilter(obj, event)
    
    def show_form(self, patient):
        self.patient_to_update = patient
        self.template_bytes = None
        self.name_input.setText(patient.get("name", ""))
        self.mobile_input.setText(patient.get("mobile", ""))
        self.age_input.setText(str(patient.get("age", "")))
        self.problem_input.setText(patient.get("problem", ""))

        department = patient.get("department", "")
        if department == "Neurologist":
            self.dep1_radio.setChecked(True)
        elif department == "Cardiologist":
            self.dep2_radio.setChecked(True)
            
        gender = patient.get("gender", "Male")
        if gender == "Male":
            self.male_radio.setChecked(True)
        else:
            self.female_radio.setChecked(True)

        parent = self.parent()
        if parent:
            self.move(
                (parent.width() - self.width()) // 2,
                (parent.height() - self.height()) // 2
            )

        self.show()
        self.raise_()

    def cancel_update(self):
        self.fingerprint_status.clear()
        self.hide()

    def save_updated_patient(self):
        name = self.name_input.text().strip()
        mobile = self.mobile_input.text().strip()
        age = self.age_input.text().strip()
        gender = "Male" if self.male_radio.isChecked() else "Female"
        problem = self.problem_input.text().strip()

        department = ""
        if self.dep1_radio.isChecked():
            department = "Neurologist"
        elif self.dep2_radio.isChecked():
            department = "Cardiologist"

        if not name or not mobile or not gender:
            ToastNotification.show_toast(
                parent=self.parent(),
                toast_type="warning",
                title="Validation Error",
                message="Complete form."
            )
            return
        
        if self.template_bytes:
            existing_patient = self.is_fingerprint_already_registered()
            if existing_patient:
                if existing_patient["_id"] != self.patient_to_update["_id"]:
                    self.update_fingerprint_status(
                        "Fingerprint Already Registered",
                        "#DC2626"
                    )
                    return
        try:
            success = self.patient_repository.update_patient(
                self.patient_to_update["_id"],
                name,
                mobile,
                age,
                gender,
                department,
                problem,  
                self.template_bytes
            )

            if success:
                self.patient_updated.emit()
                self.hide()
                ToastNotification.show_toast(
                    parent=self.parent(),
                    toast_type="success",
                    title="Success",
                    message="Patient updated successfully.",
                    duration=3000
                )
                self.fingerprint_status.clear()
            else:
                self.fingerprint_status.clear()
                self.hide()
        except DatabaseConnectionError as error:
            ToastNotification.show_toast(self, "error", "Connection Error", str(error))
            return
        
    def update_fingerprint_status(self, message, color="#64748B"):
        self.fingerprint_status.setText(message)
        self.fingerprint_status.setStyleSheet(f"""
        QLabel{{
            color:{color};
            font-size:13px;
            font-weight:600;
            border:none;
        }}
        """)
        
    def is_fingerprint_already_registered(self):
        try:
            organization_id = Session.organization_id
            patients = self.patient_repository.get_all_by_organization(organization_id)
            if not self.verification.initialize_matching():
                return None
            try:
                for patient in patients:
                    stored_template = patient.get("fingerprint_template")
                    if not stored_template:
                        continue
                    stored_template = bytes(stored_template)
                    score = self.verification.match_template(
                        self.template_bytes,
                        stored_template)
                    if score >= 100:
                        return patient
                return None
            finally:
                self.verification.terminate_matching()
        except Exception:
            return None

    def capture_fingerprint(self):
        if not self.scanner.load_sdk():
            self.template_bytes = None
            self.update_fingerprint_status("SDK Load Failed", "#DC2626")
            return

        if not self.scanner.create():
            self.template_bytes = None
            self.update_fingerprint_status("Scanner Create Failed", "#DC2626")
            return

        if not self.scanner.initialize():
            self.template_bytes = None
            self.update_fingerprint_status("Scanner Initialization Failed", "#DC2626")
            return
        
        self.scanner.sdk.SGFPM_SetTemplateFormat(self.scanner.hfpm, 0x0200)

        if not self.scanner.open_device():
            self.template_bytes = None
            self.update_fingerprint_status("Scanner Not Connected", "#DC2626")
            return

        self.update_fingerprint_status("Place Finger On Scanner", "#2563EB")
        image, message = self.scanner.capture_image()
        
        if not image:
            self.template_bytes = None            
            if message and ("not clear" in message.lower() or "low" in message.lower()):
                self.update_fingerprint_status("Image Not Clear. Try Again!", "#DC2626")
            else:
                error_msg = message if message else "Capture Failed"
                self.update_fingerprint_status(error_msg, "#DC2626")
                
            self.scanner.close_device()
            self.scanner.terminate()
            return

        self.template_bytes = self.enrollment.create_template_bytes(image)
        if not self.template_bytes:
            self.template_bytes = None 
            self.update_fingerprint_status("Try again", "#EA580C")
            self.scanner.close_device()
            self.scanner.terminate()
            return

        self.update_fingerprint_status("Fingerprint Captured ✓", "#16A34A")
        self.scanner.close_device()
        self.scanner.terminate()