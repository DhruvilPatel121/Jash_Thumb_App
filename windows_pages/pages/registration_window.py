import os
from PyQt6.QtWidgets import (QWidget,QButtonGroup,QHBoxLayout,QVBoxLayout,QPushButton,QFrame, QLabel, QRadioButton,QTableWidget, QTableWidgetItem,QHeaderView,QAbstractItemView,QComboBox)
from PyQt6.QtCore import Qt,QDateTime,QTimer,QEvent,QSize
from PyQt6.QtGui import QPixmap,QMovie
from PyQt6.QtWidgets import QFormLayout, QLineEdit
from utils.toast_notification import ToastNotification
from PyQt6.QtWidgets import QSizePolicy
from utils.scanner_manager import ScannerManager
from utils.enrollment import Enrollment
from utils.verification import Verification
from utils.session import Session
from database.patient_repository import PatientRepository
from database.mongodb_connection import DatabaseConnectionError
from PyQt6.QtCore import pyqtSignal

class RegistrationPage(QWidget):

    patient_registered = pyqtSignal()

    def __init__(self, db=None):
        super().__init__()

        self.db = db
        self.setup_ui()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_date_time)
        self.timer.start(1000)
        self.template_bytes = None

        self.scanner = ScannerManager()
        self.enrollment = Enrollment(self.scanner)
        self.verification = Verification(self.scanner)
        self.patient_repository = PatientRepository()
        
        self.template_bytes = None
        self.gender_sequence_active = False

    def showEvent(self, event):
        super().showEvent(event)
        self.reset_scanner_ui()

    def reset_scanner_ui(self):
        self.template_bytes = None
        self.device_status.setText("Device Status : Ready 🟢")
        self.update_scan_status(
                "assets/fingerscan.gif",
                "Ready To Scan",
                "#3B82F6"
        )
        self.capture_status.setText("Place your finger on the scanner")

    def setup_ui(self):
        # Main Layout
        self.main_layout = QHBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.setLayout(self.main_layout)

        # Content Area - Changed to off-white theme
        self.content_area = QFrame()
        self.content_area.setStyleSheet("""
            QFrame{
                background-color: #F8FAFC;
            }
        """)

        # Add to Main Layout
        self.main_layout.addWidget(self.content_area)

        # contentlayout create
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(50, 40, 50, 40) # Adjusted margins for better page framing
        self.content_layout.setSpacing(30)
        self.content_area.setLayout(self.content_layout)

        # Header Layout
        self.header_layout = QHBoxLayout()

        # heading page
        self.page_title = QLabel("Registration")
        self.page_title.setStyleSheet("""
            QLabel{
                color: #1E293B; /* Dark Slate text */
                font-size: 32px;
                font-weight: bold;
            }
        """)

        # Date
        self.date_label = QLabel("📅 08 Jun 2026")
        self.date_label.setStyleSheet("""
        QLabel{
            color: #64748B;
            font-size: 18px;
            font-weight: 600;
        }
        """)

        # Time
        self.time_label = QLabel("🕒 03:35 PM")
        self.time_label.setStyleSheet("""
        QLabel{
            color: #64748B;
            font-size: 18px;
            font-weight: 600;
        }
        """)

        # Username
        self.user_label = QLabel("👤 Admin")
        self.user_label.setStyleSheet("""
        QLabel{
            color: #64748B;
            font-size: 18px;
            font-weight: 600;
        }
        """)
        self.header_layout.addWidget(self.page_title)
        self.header_layout.addStretch()
        self.header_layout.addWidget(self.date_label)
        self.header_layout.addSpacing(20)
        self.header_layout.addWidget(self.time_label)
        self.header_layout.addSpacing(20)
        self.header_layout.addWidget(self.user_label)
        self.content_layout.addLayout(self.header_layout)


        #registration body part where have detail and device status card
        self.body_layout = QHBoxLayout()
        self.body_layout.setSpacing(20)
        self.content_layout.addLayout(self.body_layout)

        #body-1.1 detail
        self.patient_detail_card = QFrame()
        self.patient_detail_card.setObjectName("patientCard")
        self.patient_detail_card.setStyleSheet("""
            #patientCard{
                background-color: #FFFFFF; /* Pure white card */
                border: 1px solid #E2E8F0; /* Soft border */
                border-radius: 16px;
            }
        """)
        self.body_layout.addWidget(self.patient_detail_card, 6)

        #new layout in detail card
        self.patient_layout = QVBoxLayout()
        self.patient_layout.setContentsMargins(25, 25, 25, 25)
        self.patient_layout.setSpacing(20)

        #add heading 
        self.patient_detail_card.setLayout(self.patient_layout)
        self.patient_title = QLabel(" Patient Information")
        self.patient_title.setStyleSheet("""
            QLabel{
                color: #1E293B; /* Teal Accent */
                background-color: transparent;
                font-size: 18px;
                font-weight: bold;
                border: none;
            }
        """)
        self.patient_layout.addWidget(self.patient_title)

        #form layout
        self.form_layout = QFormLayout()
        self.form_layout.setHorizontalSpacing(30)
        self.form_layout.setVerticalSpacing(20)
        self.patient_layout.addLayout(self.form_layout)

        #create label
        self.name_label = QLabel("Full Name")
        self.email_label = QLabel("Email Address")
        self.mobile_label = QLabel("Phone Number")
        self.age_label = QLabel("Age")
        self.gender_label = QLabel("Gender")
        self.department_label = QLabel("Department")
        self.problem_label = QLabel("Problem")

        label_style = """
        QLabel{
            color: #334155; /* Medium Slate */
            font-size: 14px;
            font-weight: 500;
            border: none;
            background: transparent;
        }
        """

        for lbl in [
                self.name_label,
                self.email_label,
                self.mobile_label,
                self.age_label,
                self.gender_label,
                self.department_label,
                self.problem_label
            ]:
            lbl.setStyleSheet(label_style)
            lbl.setFixedWidth(120)
            lbl.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

            
        #input field
        self.name_input = QLineEdit()
        self.email_input = QLineEdit()
        self.mobile_input = QLineEdit()
        self.age_input = QLineEdit()
        self.name_input.setPlaceholderText("   Enter full name")
        self.email_input.setPlaceholderText("   Enter email address")
        self.mobile_input.setPlaceholderText("   Enter phone number")
        self.mobile_input.setMaxLength(10)
        self.age_input.setPlaceholderText("   Enter Age")
        self.age_input.setMaxLength(3)
        self.neuro_radio = QRadioButton("Neurologist")
        self.cardio_radio = QRadioButton("Cardiologist")
        self.dept_group = QButtonGroup()
        self.dept_group.addButton(self.neuro_radio)
        self.dept_group.addButton(self.cardio_radio)
        self.department_layout = QHBoxLayout()
        self.department_layout.setSpacing(20)
        self.department_layout.addWidget(self.neuro_radio)
        self.department_layout.addWidget(self.cardio_radio)
        self.department_layout.addStretch()
        self.male_radio = QRadioButton("Male")
        self.female_radio = QRadioButton("Female")
        self.gender_group = QButtonGroup()
        self.gender_group.addButton(self.male_radio)
        self.gender_group.addButton(self.female_radio)
        gender_layout = QHBoxLayout()
        gender_layout.setSpacing(20)
        gender_layout.addWidget(self.male_radio)
        gender_layout.addWidget(self.female_radio)
        radio_button_style = """
        QRadioButton{
            color:black;
            font-size:14px;
            font-weight:600;
            background:transparent;
            spacing:8px;
            padding:4px;
        }

        QRadioButton:focus{
            border:2px solid #4F46E5;
            border-radius:6px;
            background-color:#EEF2FF;
        }

        QRadioButton::indicator{
            width:18px;
            height:18px;
            border:2px solid #94A3B8;
            border-radius:9px;
            background:white;
        }

        QRadioButton::indicator:checked{
            background-color:#4F46E5;
            border:2px solid #4F46E5;
        }
        """

        self.male_radio.setStyleSheet(radio_button_style)
        self.female_radio.setStyleSheet(radio_button_style)
        self.neuro_radio.setStyleSheet(radio_button_style)
        self.cardio_radio.setStyleSheet(radio_button_style)
        gender_layout.addStretch()
        self.problem_input = QLineEdit()
        self.problem_input.setPlaceholderText(
            "Describe patient problem..."
        )
        input_style = """
        QLineEdit{
            background-color: #FFFFFF;
            color: #1E293B;
            border: 1px solid #E2E8F0;
            border-radius: 8px;
            padding: 10px 15px;
            font-size: 14px;
        }

        QLineEdit:focus{
            border: 2px solid #5C62D6; /* Teal focus border */
        }
        """

        for widget in [
            self.name_input,
            self.email_input,
            self.mobile_input,
            self.age_input,
            self.problem_input
        ]:
            widget.setStyleSheet(input_style)
            widget.setSizePolicy(
                QSizePolicy.Policy.Expanding,
                QSizePolicy.Policy.Fixed
            )

        #add all the field in layout
        self.form_layout.addRow(self.name_label, self.name_input)
        self.form_layout.addRow(self.email_label, self.email_input)
        self.form_layout.addRow(self.mobile_label, self.mobile_input)
        self.form_layout.addRow(self.age_label, self.age_input)
        
        self.form_layout.addRow(
            self.gender_label,
            gender_layout
        )
        self.form_layout.addRow(self.department_label, self.department_layout)
        self.form_layout.addRow(
            self.problem_label,
            self.problem_input
        )
        self.patient_layout.addStretch()


        #body-1.2 status
        self.device_status_card = QFrame()
        self.device_status_card.setStyleSheet("""
            QFrame{
                background-color: #FFFFFF; /* Pure white card */
                border: 1px solid #E2E8F0;
                border-radius: 16px;
            }
        """)
        self.body_layout.addWidget(self.device_status_card, 4)
        self.patient_detail_card.setMinimumHeight(500)
        self.device_status_card.setMinimumHeight(500)
        #fingerprint card layout
        self.fingerprint_layout = QVBoxLayout()
        self.fingerprint_layout.setContentsMargins(25,25,25,25)
        self.fingerprint_layout.setSpacing(20)
        self.device_status_card.setLayout(self.fingerprint_layout)
        self.fingerprint_title = QLabel("Fingerprint Registration")
        self.fingerprint_title.setStyleSheet("""
            QLabel{
                color: #1E293B; /* Teal Accent */
                font-size: 18px;
                font-weight: bold;
                border: none;
                background: transparent;
            }
        """)

        self.fingerprint_layout.addWidget(self.fingerprint_title)
        self.device_status = QLabel("Device Status : <span style='color:#16A34A; font-weight:bold;'></span>")
        self.device_status.setTextFormat(Qt.TextFormat.RichText)
        self.device_status.setStyleSheet("""
            QLabel{
                color: #334155;
                font-size: 14px;
                border: none;
                background: transparent;
            }
        """)

        self.fingerprint_layout.addWidget(self.device_status)
        self.status_card = QFrame()
        self.status_card.setStyleSheet("""
        QFrame{
            background-color: #F8FAFC;
            border: 1px solid #E2E8F0;
            border-radius: 12px;
        }
        """)

        self.status_layout = QVBoxLayout()
        self.status_layout.setContentsMargins(20,20,20,20)
        self.status_layout.setSpacing(10)
        self.status_card.setLayout(self.status_layout)
        self.scan_icon = QLabel()
        self.scan_text = QLabel()
        self.scan_icon = QLabel()
        self.scan_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.scan_icon.setStyleSheet("""
        QLabel{
            font-size: 64px;
            border:none;
        }
        """)
        self.scan_text = QLabel("Ready To Scan")
        self.scan_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.scan_text.setStyleSheet("""
        QLabel{
            color:#3B82F6;
            font-size:18px;
            font-weight:600;
            border:none;
        }
        """)
        self.status_layout.addStretch()
        self.status_layout.addWidget(self.scan_icon)
        self.status_layout.addWidget(self.scan_text)
        self.status_layout.addStretch()
        self.fingerprint_layout.addWidget(self.status_card)
        self.capture_status = QLabel("Place your finger on the scanner\n<span style='color:#3B82F6;'></span>")
        self.capture_status.setTextFormat(Qt.TextFormat.RichText)
        self.capture_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.capture_status.setStyleSheet("""
            QLabel{
                color: #64748B;
                font-size: 13px;
                border: none;
                background: transparent;
            }
        """)
        
        self.fingerprint_layout.addWidget(self.capture_status)
        self.capture_btn = QPushButton("Start Scanner")
        self.capture_btn.setFixedHeight(50)
        self.capture_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.capture_btn.setDefault(True)
        self.capture_btn.setStyleSheet("""
            QPushButton{
                background-color: #5C62D6; /* Solid Teal matching image */
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 15px;
                font-weight: bold;
            }

            QPushButton:hover{
            background-color: #4C51BF;
            }
            QPushButton:pressed{
                border: 1px solid #1D4ED8;
                padding-top: 3px;
                padding-left: 3px;
            }
            """)
        self.capture_btn.clicked.connect(self.capture_fingerprint)
        self.clear_scan_btn = QPushButton("↻ Clear")
        self.clear_scan_btn.setFixedHeight(50)
        self.clear_scan_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clear_scan_btn.setStyleSheet("""
        QPushButton{
            background-color: #F8F9FA;
            color: #64748B;
            border: 1px solid #E2E8F0;
            border-radius: 8px;
            font-size: 15px;
            font-weight: bold;
        }

        QPushButton:hover{
            background-color: #F1F5F9;
            color: #334155;
        }
        QPushButton:pressed{
            border: 1px solid #1D4ED8;
            padding-top: 3px;
            padding-left: 3px;
        }
        """)

        self.clear_scan_btn.clicked.connect(self.clear_fingerprint_scan)
        capture_button_layout = QHBoxLayout()
        capture_button_layout.addWidget(self.capture_btn,3)
        capture_button_layout.addWidget(self.clear_scan_btn,1)
        self.fingerprint_layout.addLayout(capture_button_layout)
        self.fingerprint_layout.addStretch()

        #button layout
        self.button_layout = QHBoxLayout()
        self.button_layout.setSpacing(15)
        self.content_layout.addLayout(self.button_layout)

        #create save and clear button
        self.save_btn = QPushButton("Save Patient")
        self.save_btn.setFixedSize(200, 50)
        self.save_btn.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Fixed
        )
        self.save_btn.clicked.connect(self.save_patient)
        self.save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.save_btn.setStyleSheet("""
                QPushButton{
                background-color: #5C62D6;
                color: white;
                border: none;
                border-radius: 10px;Fsearch
                font-size: 14px;
                font-weight: 600;
            }

            QPushButton:hover{
                background-color: #4C51BF;
            }
            QPushButton:pressed{
                border: 1px solid #1D4ED8;
                padding-top: 3px;
                padding-left: 3px;
            }
            """)   

        self.clear_btn = QPushButton("↻ Clear")
        self.clear_btn.setFixedSize(150, 50)
        self.clear_btn.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Fixed
        )
        self.clear_btn.clicked.connect(self.clear_registration_form)
        self.clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clear_btn.setStyleSheet("""
            QPushButton{
            background-color: #F8F9FA;
            color: #64748B;
            border: 1px solid #E2E8F0;
            border-radius: 8px;
            font-size: 15px;
            font-weight: bold;
        }

        QPushButton:hover{
            background-color: #F1F5F9;
            color: #334155;
        }
        QPushButton:pressed{
            border: 1px solid #1D4ED8;
            padding-top: 3px;
            padding-left: 3px;
        }
        """)

        self.button_layout.addStretch()
        self.button_layout.addWidget(self.save_btn)
        self.button_layout.addWidget(self.clear_btn)
        self.button_layout.addStretch()
        self.content_layout.addStretch()


        # NEW FOOTER CODE ADDED HERE
        self.footer_layout = QHBoxLayout()
        self.footer_layout.setContentsMargins(0, 15, 0, 0)
        self.footer_label = QLabel("Handicraft By Shivvilon Solution")
        self.footer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.footer_label.setStyleSheet("""
            QLabel {
                color: #94A3B8; /* Light slate gray */
                font-size: 13px;
                font-weight: 500;
                letter-spacing: 0.5px;
            }
        """)
        self.footer_layout.addWidget(self.footer_label)
        self.content_layout.addLayout(self.footer_layout)

        self.age_input.installEventFilter(self)
        self.male_radio.installEventFilter(self)
        self.female_radio.installEventFilter(self)
        self.neuro_radio.installEventFilter(self)
        self.cardio_radio.installEventFilter(self)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.KeyPress:
            if event.key() == Qt.Key.Key_Tab:
                if obj == self.age_input:
                    self.gender_sequence_active = True
                    self.male_radio.setFocus()
                    return True

                if self.gender_sequence_active:
                    if obj == self.male_radio:
                        self.female_radio.setFocus()
                        return True

                    elif obj == self.female_radio:
                        self.neuro_radio.setFocus()
                        return True

                    elif obj == self.neuro_radio:
                        self.cardio_radio.setFocus()
                        return True

                    elif obj == self.cardio_radio:
                        self.gender_sequence_active = False
                        self.problem_input.setFocus()
                        return True

        return super().eventFilter(obj, event)

    def validate_registration(self):
        name = self.name_input.text().strip()
        mobile = self.mobile_input.text().strip()
        gender = (self.male_radio.isChecked() or self.female_radio.isChecked())

        if (not name or not mobile or not gender):
            ToastNotification.show_toast(
                self,
                "warning",
                "Incomplete Form",
                "Please fill Name,Number and Gender fields."
            )
            return False 
            
        if not self.template_bytes:
            ToastNotification.show_toast(
                self,
                "warning",
                "Fingerprint Required",
                "Please scan fingerprint first."
            )
            return False
        return True
            
    
    def capture_fingerprint(self):
        
        if not self.scanner.load_sdk():
            ToastNotification.show_toast(
                self,
                "error",
                "SDK Load Failed",
                "Unable to load scanner SDK."
            )
            self.reset_scanner_ui()
            return

        if not self.scanner.create():
            ToastNotification.show_toast(
                self,
                "error",
                "Scanner Create Failed",
                "Unable to create scanner object."
            )
            self.reset_scanner_ui()
            return

        if not self.scanner.initialize():
            ToastNotification.show_toast(
                self,
                "error",
                "Initialization Failed",
                "Unable to initialize scanner."
            )
            self.reset_scanner_ui()
            return

        self.scanner.sdk.SGFPM_SetTemplateFormat(self.scanner.hfpm,0x0200)

        if not self.scanner.open_device():
            self.device_status.setText(
                "Device Status : Disconnected 🔴"
            )

            self.update_scan_status(
            "assets/Disconnect.gif", 
            "Scanner Not Found",
            "#2563EB")

            self.capture_status.setText(
                "Please connect the fingerprint scanner."
            )
            return
        image, message = self.scanner.capture_image()
        if not image:

            self.update_scan_status(
            "assets/Fingerprint_capture_fail.gif", 
            "Capture Fail",
            "#EF4444"
            )
            self.capture_status.setText(message)
            if "not clear" in message.lower() or "low" in message.lower():
                    self.update_scan_status(
                    "assets/Wrong fingerprint.gif", 
                    "Image not Clear",
                    "#EF4444"
                    )
            self.scanner.close_device()
            self.scanner.terminate()
            return

        self.template_bytes = (self.enrollment.create_template_bytes(image))
        if not self.template_bytes:
            self.update_scan_status(
                "⚠️",
                "Template Failed",
                "#EA580C"
            )
            self.capture_status.setText("Please scan again.")
            self.scanner.close_device()
            self.scanner.terminate()
            return

        self.update_scan_status(
            "assets/Fingerprint biometric success.gif", 
            "Fingerprint Captured",
            "#2563EB"
        )
        self.capture_status.setText("Ready to save.")
        self.scanner.close_device()
        self.scanner.terminate()

    def is_fingerprint_already_registered(self):
        try:
            organization_id = Session.organization_id

            patients = (
                self.patient_repository
                .get_all_by_organization(
                    organization_id))
            if not self.verification.initialize_matching():
                return None
            try:
                for patient in patients:
                    stored_template = bytes(
                        patient["fingerprint_template"]
                    )
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


    def save_patient(self):
        if not self.validate_registration():
            return
        organization_id = (Session.organization_id)
        name = self.name_input.text().strip()
        email = self.email_input.text().strip()
        mobile = self.mobile_input.text().strip()
        age = self.age_input.text().strip()
        gender = ("Male" if self.male_radio.isChecked() else "Female")
        department = ""
        if self.neuro_radio.isChecked():
            department = "Neurologist"
        elif self.cardio_radio.isChecked():
            department = "Cardiologist"
        problem = self.problem_input.text().strip()

        try:
            mobile = self.mobile_input.text().strip()
            is_mobile_exist = self.patient_repository.is_mobile_registered(mobile)
            if is_mobile_exist:
                ToastNotification.show_toast(
                    self,
                    "warning",
                    "Mobile Already Registered",
                    f"The number {mobile} is already in use."
                )
                return
            
            existing_patient =self.is_fingerprint_already_registered()
            if existing_patient:
                ToastNotification.show_toast(
                    self,
                    "warning",
                    "Patient Already Registered",
                    f"{existing_patient['name']} already exists."
                )
                self.clear_registration_form()
                return

            patient_id = self.patient_repository.create_patient(
                organization_id,
                name,
                email,
                mobile,
                age,
                gender,
                department,
                problem,
                self.template_bytes
            )
            if patient_id:
                self.patient_registered.emit()
                ToastNotification.show_toast(
                    self,
                    "success",
                    "Patient Registered",
                    "Patient registered successfully."
                )
                self.clear_registration_form()

            else:
                ToastNotification.show_toast(
                    self,
                    "error",
                    "Registration Failed",
                    "Unable to save patient."
                )
        except DatabaseConnectionError as error:
            ToastNotification.show_toast(
                self,
                "error",
                "Connection Error",
                str(error))
            return

    def update_date_time(self):
        current_datetime = QDateTime.currentDateTime()
        current_date = current_datetime.toString("dd MMM yyyy")
        current_time = current_datetime.toString("hh:mm:ss AP")
        self.date_label.setText(f"📅 {current_date}")
        self.time_label.setText(f"🕒 {current_time}")

    def clear_registration_form(self):

        self.name_input.clear()
        self.email_input.clear()
        self.mobile_input.clear()
        self.age_input.clear()
        self.problem_input.clear()
        self.gender_group.setExclusive(False)
        self.male_radio.setChecked(False)
        self.female_radio.setChecked(False)
        self.gender_group.setExclusive(True)
        self.dept_group.setExclusive(False)
        self.neuro_radio.setChecked(False)
        self.cardio_radio.setChecked(False)
        self.dept_group.setExclusive(True)    
        self.template_bytes = None
        self.gender_sequence_active = False
        self.reset_scanner_ui()
        self.name_input.setFocus()

    def clear_fingerprint_scan(self):
        try:
            self.scanner.close_device()
            self.scanner.terminate()
        except:
            pass
        finally:
            self.reset_scanner_ui()


    def update_scan_status(self, source, message, color="#3B82F6"):
        # જો કોઈ જૂનું GIF એનિમેશન ચાલુ હોય, તો તેને બંધ કરો (Memory બચાવવા)
        if hasattr(self, 'movie') and self.movie is not None:
            self.movie.stop()
            self.movie = None
            
        self.scan_icon.clear()

        if os.path.exists(source):
            if source.lower().endswith('.gif'):
                self.movie = QMovie(source)
                self.movie.setScaledSize(QSize(140, 140))
                self.movie.setSpeed(200)
                self.scan_icon.setMovie(self.movie)
                def stop_if_last_frame(frame_number):
                    if frame_number == self.movie.frameCount() - 1:
                        self.movie.setPaused(True)
                
                self.movie.frameChanged.connect(stop_if_last_frame)
                self.movie.start()
            else:
                pixmap = QPixmap(source)
                scaled_pixmap = pixmap.scaled(
                    140, 140, 
                    Qt.AspectRatioMode.KeepAspectRatio, 
                    Qt.TransformationMode.SmoothTransformation
                )
                self.scan_icon.setPixmap(scaled_pixmap)
        else:
            self.scan_icon.setText(source)
            self.scan_icon.setStyleSheet("""
            QLabel{
                font-size: 64px;
                border: none;
                background: transparent;
            }
            """)
        
        self.scan_text.setText(message)
        self.scan_text.setStyleSheet(f"""
        QLabel{{
            color: {color};
            font-size: 18px;
            font-weight: 600;
            border: none;
            background: transparent;
        }}
        """)