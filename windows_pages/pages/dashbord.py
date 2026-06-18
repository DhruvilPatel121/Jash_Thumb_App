from PyQt6.QtWidgets import (QWidget,QLineEdit,QHBoxLayout,QSizePolicy,QVBoxLayout,QPushButton,QFrame, QLabel, QTableWidget, QTableWidgetItem,QHeaderView,QAbstractItemView)
from PyQt6.QtCore import Qt, QTimer, QDateTime
from PyQt6.QtWidgets import QAbstractItemView
from utils.toast_notification import (ToastNotification,PatientSuccessModal)
from database.attendance_worker import (AttendanceWorker)
from datetime import datetime
from utils.session import Session

class DashboardPage(QWidget):

    def __init__(self, db=None):
        super().__init__()
        self.setup_ui()
        self.db = db
        self.attendance_worker = AttendanceWorker()
        self.attendance_worker.scanner_connected.connect(self.on_scanner_connected)
        self.attendance_worker.scanner_connection_failed.connect(self.on_scanner_connection_failed)
        self.attendance_worker.scanner_disconnected.connect(self.on_scanner_disconnected)
        self.attendance_worker.attendance_marked.connect(self.on_attendance_marked)
        self.attendance_worker.already_taken.connect(self.on_already_taken)
        self.attendance_worker.patient_not_found.connect(self.on_patient_not_found)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_date_time)
        self.timer.start(1000)
        self.scanner_running = False

    def setup_ui(self):

        # Main Layout
        self.main_layout = QHBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.setLayout(self.main_layout)

        # Content Area - Changed to light off-white theme
        self.content_area = QFrame()
        self.content_area.setStyleSheet("""
            QFrame{
                background-color: #F8FAFC;
            }
        """)

        # Add to Main Layout
        self.main_layout.addWidget(self.content_area)

        # Header content layout
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(40, 40, 40, 40) # Increased margins for a cleaner look
        self.content_layout.setSpacing(20)
        self.content_area.setLayout(self.content_layout)

        self.page_title = QLabel("Attendance Dashboard")
        self.page_title.setStyleSheet("""
            QLabel{
                color: #1E293B; /* Dark Slate */
                font-size: 28px;
                font-weight: 700;
                font-weight: bold;
            }
        """)

        # Header Layout
        self.header_layout = QHBoxLayout()

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

        # Statistics Cards
        self.cards_layout = QHBoxLayout()
        self.cards_layout.setSpacing(20)
        self.content_layout.addLayout(self.cards_layout)

        cards = [
            ("Today's Visit", "0", "#FFFFFF", "#16A34A"),
            ("Total Patient", "0", "#FFFFFF", "#5C62D6")
        ]

        for card_title, card_value, bg_color, text_color in cards:

            card = QFrame()
            card.setStyleSheet(f"""
                QFrame{{
                    background-color: {bg_color};
                    border: 1px solid #E2E8F0;
                    border-radius: 16px;
                }}
            """)
            card.setFixedHeight(130)

            layout = QVBoxLayout()
            layout.setContentsMargins(20, 20, 20, 20)
            layout.setSpacing(5)

            title = QLabel(card_title)
            title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            title.setStyleSheet("""
                QLabel{
                    color: #64748B; /* Slate Gray */
                    font-size: 15px;
                    font-weight: bold;
                    border: none;
                    background: transparent;
                }
            """)

            count = QLabel(card_value)

            count.setAlignment(
                Qt.AlignmentFlag.AlignCenter
            )

            count.setStyleSheet(f"""
                QLabel{{
                    color: {text_color};
                    font-size: 38px;
                    font-weight: bold;
                    border: none;
                    background: transparent;
                }}
            """)

            if card_title == "Today's Visit":
                self.visited_today_count = count

            elif card_title == "Total Patient":
                self.total_patient_count = count
            
            layout.addStretch()
            layout.addWidget(title)
            layout.addWidget(count)
            layout.addStretch()
            card.setLayout(layout)
            self.cards_layout.addWidget(card, 1)


        #table formate and headings
        self.attendance_title = QLabel("Detailed Attendance Logs")
        self.attendance_title.setStyleSheet("""
            QLabel{
                    color: #1E293B; /* Dark Slate */
                    font-size: 20px;
                    font-weight: bold;
                    margin-top: 15px;
                }
            """)
        self.attendance_title.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.content_layout.addWidget(self.attendance_title)

        #searchbox 
        self.search_layout = QHBoxLayout()
        self.search_layout.setSpacing(15)
        self.content_layout.addLayout(self.search_layout)
        self.search_input = QLineEdit()
        self.search_input.textChanged.connect(self.search_attendance_logs)
        self.search_input.setPlaceholderText("Search patient...")
        self.search_input.setFixedHeight(45)
        self.search_input.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Fixed)
        self.search_input.setStyleSheet("""
        QLineEdit{
            background-color: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 10px;
            padding-left: 15px;
            font-size: 14px;
            color: #334155;
        }

        QLineEdit:focus{
            border: 2px solid #5C62D6;
        }
        """)

        self.scanner_btn = QPushButton("Start Scanner")
        self.scanner_btn.setFixedSize(160,50)
        self.scanner_btn.clicked.connect(self.start_scanner)
        self.scanner_btn.setStyleSheet("""
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
        self.search_layout.addWidget(self.search_input,1)
        self.search_layout.addStretch()
        self.search_layout.addWidget(self.scanner_btn)

       
        self.table_frame = QFrame()
        self.table_frame.setObjectName("tableFrame")
        # self.table_frame.setFixedHeight(450) <-- Aa line kadhi nakhi jethi screen mujab adjust thai
        self.table_frame.setStyleSheet("""
        QFrame#tableFrame { 
            background-color: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 16px;
        }
        """)
        self.content_layout.addWidget(self.table_frame, 1) # '1' stretch factor add karyo jethi perfect fit thai
        
        # Horizontal layout for the two departments
        dual_table_layout = QHBoxLayout()
        dual_table_layout.setContentsMargins(15, 15, 15, 15)
        dual_table_layout.setSpacing(20) 
        self.table_frame.setLayout(dual_table_layout)

        # Neurologist Layout
        left_layout = QVBoxLayout()
        left_title = QLabel("Neurologist Department")
        left_title.setStyleSheet("QLabel{ color: #1E293B; font-size: 18px; font-weight: bold; margin-bottom: 5px; }")
        left_layout.addWidget(left_title)
        self.neuro_table = self.create_styled_table()
        left_layout.addWidget(self.neuro_table)
        
        # Cardiologist Layout
        right_layout = QVBoxLayout()
        right_title = QLabel("Cardiologist Department")
        right_title.setStyleSheet("QLabel{ color: #1E293B; font-size: 18px; font-weight: bold; margin-bottom: 5px; }")
        right_layout.addWidget(right_title)
        self.cardio_table = self.create_styled_table()
        right_layout.addWidget(self.cardio_table)
        dual_table_layout.addLayout(left_layout)
        dual_table_layout.addLayout(right_layout)

        # NEW FOOTER CODE
        self.footer_layout = QHBoxLayout()
        self.footer_layout.setContentsMargins(0, 10, 0, 0)
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
        # ==========================================

    def create_styled_table(self):
        """Helper function to create a table with your exact old styling and new columns."""
        table = QTableWidget()
        table.setColumnCount(6) # Now 6 columns
        table.setHorizontalHeaderLabels(["#", "Patient Name", "Check In", "Mobile Number", "Age", "Problem"])
        
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        table.setShowGrid(False)
        table.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        table.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        table.verticalHeader().setVisible(False)
        table.verticalHeader().setDefaultSectionSize(50)
        table.setFrameShape(QFrame.Shape.NoFrame)
        table.setFrameShadow(QFrame.Shadow.Plain)

        table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        table.setStyleSheet("""
            /* --- TABLE BASE STYLING --- */
            QTableWidget { 
                background-color: #FFFFFF; 
                border: none; 
                outline: 0; 
                color: #334155; 
                font-size: 14px; 
            }
            QTableWidget::item { 
                padding: 8px; 
                border-bottom: 1px solid #EDF2F7; 
            }
            QHeaderView::section { 
                background-color: #FFFFFF; 
                color: #475569; 
                border: none; 
                border-bottom: 1px solid #E2E8F0;
                margin: 0px; 
                padding: 10px 5px; 
                font-size: 15px; 
                font-weight: 600; 
            }
            QTableCornerButton::section { 
                background-color: #FFFFFF; 
                border: none; 
            }

            /* --- MODERN VERTICAL SCROLLBAR --- */
            QScrollBar:vertical {
                border: none;
                background: transparent;
                width: 8px; /* Thinner bar */
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #CBD5E1; /* Nice light slate gray */
                min-height: 30px;
                border-radius: 4px; /* Rounded corners */
            }
            QScrollBar::handle:vertical:hover {
                background: #94A3B8; /* Darkens slightly when mouse is over */
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px; /* Completely hides the ugly up/down arrow buttons */
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none; /* Removes the dark track background */
            }

            /* --- MODERN HORIZONTAL SCROLLBAR --- */
            QScrollBar:horizontal {
                border: none;
                background: transparent;
                height: 8px; /* Thinner bar */
                margin: 0px;
            }
            QScrollBar::handle:horizontal {
                background: #CBD5E1;
                min-width: 30px;
                border-radius: 4px;
            }
            QScrollBar::handle:horizontal:hover {
                background: #94A3B8;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px; /* Completely hides the ugly left/right arrow buttons */
            }
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
                background: none;
            }
        """)

        # Header Alignment & Sizing
        header = table.horizontalHeader()
        header.setHighlightSections(False)
        header.setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setFixedHeight(50)
        
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        header.setMinimumSectionSize(60)
        
        table.setColumnWidth(0, 30)   # #
        table.setColumnWidth(1, 200)  # Patient Name
        table.setColumnWidth(2, 90)   # Check In
        table.setColumnWidth(3, 120)  # Mobile
        table.setColumnWidth(4, 50)   # Age
        table.setColumnWidth(5, 150)  # Problem

        return table

    def load_today_logs(self, search_text=None):
        # Clear both new tables
        self.neuro_table.setRowCount(0)
        self.cardio_table.setRowCount(0)
        today_date = datetime.now().strftime("%Y-%m-%d")
        organization_id = Session.organization_id
        logs = self.attendance_worker.attendance_repository.get_today_logs(organization_id, today_date, search_text)
        neuro_row = 0
        cardio_row = 0

        for record in logs:
            department = record.get("department", "").lower().strip() 
            
            if "neurologist" in department:
                target_table = self.neuro_table
                current_row = neuro_row
                neuro_row += 1
            elif "cardiologist" in department:
                target_table = self.cardio_table
                current_row = cardio_row
                cardio_row += 1
            else:
                continue

            target_table.insertRow(current_row)
            target_table.setRowHeight(current_row, 55)

            # Insert Data
            items = [
                QTableWidgetItem(str(current_row + 1)),
                QTableWidgetItem(record.get("patient_name", "")),
                QTableWidgetItem(record.get("check_in_time", "")),
                QTableWidgetItem(record.get("mobile", "")),
                QTableWidgetItem(str(record.get("age", ""))),
                QTableWidgetItem(record.get("problem", ""))
            ]

            # Apply Center Alignment and set to table
            for col_index, item in enumerate(items):
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                target_table.setItem(current_row, col_index, item)


    def load_initial_data(self):
        self.load_dashboard_counts()
        self.load_today_logs()

    def update_date_time(self):
        current_datetime = QDateTime.currentDateTime()
        current_date = current_datetime.toString("dd MMM yyyy")
        current_time = current_datetime.toString("hh:mm:ss AP")
        self.date_label.setText(f"📅 {current_date}")
        self.time_label.setText(f"🕒 {current_time}")


        
    def on_scanner_connection_failed(self, message):
        ToastNotification.show_toast(
            parent=self,
            toast_type="error",
            title="Scanner Not Found", 
            message="Please check the USB connection and try again.", 
            duration=5000 
        )

    def start_scanner(self):
        if not self.scanner_running:
            self.attendance_worker.start_attendance()
        else:
            self.attendance_worker.stop_attendance()

    def on_scanner_connected(self):
        self.scanner_running = True
        self.scanner_btn.setText(
            "Stop Scanner"
        )
        ToastNotification.show_toast(
            parent=self,
            toast_type="success",
            title="Scanner Connected",
            message="Device is ready to scan fingerprints.",
            duration=3000 
        )
        
    def on_scanner_disconnected(self):
        self.scanner_running = False
        self.scanner_btn.setText("Start Scanner")
        ToastNotification.show_toast(
            parent=self,
            toast_type="warning",
            title="Scanner Closed",
            message="Attendance Stopped.",
            duration=3000 
        )

    def stop_scanner_on_page_change(self):
        if self.scanner_running:
            self.attendance_worker.stop_attendance()

    def on_attendance_marked(self,patient):
        PatientSuccessModal.show_modal(
            self,
            serial_no=patient.get('serial_no', 'N/A'),
            name=patient.get('name', 'Unknown'),
            age=patient.get('age', 'N/A'),
            gender=patient.get('gender', 'N/A'),
            department=patient.get('department', 'N/A'),
            problem=patient.get('problem', 'N/A'),
            duration=5000
        )
        self.load_dashboard_counts()
        self.load_today_logs()

    def on_already_taken(self, patient_name):
        ToastNotification.show_toast(
            parent=self,
            toast_type="warning",
            title="Entry Already Recorded",
            message=f"{patient_name} has already checked in today.", 
            duration=4000
        )

    def on_patient_not_found(self):
        ToastNotification.show_toast(
            parent=self,
            toast_type="error",
            title="Patient Not Found",
            message="This fingerprint is not registered in the system.",
            duration=4000
        )
    def search_attendance_logs(self):
        search_text = (self.search_input.text().strip())
        self.load_today_logs(search_text)

    def load_dashboard_counts(self):
        organization_id = (Session.organization_id)
        today_date = datetime.now().strftime("%Y-%m-%d")
        total_patients = (self.attendance_worker.patient_repository.count_patients(organization_id))
        visited_today = (self.attendance_worker.attendance_repository.count_today_attendance(organization_id,today_date))

        self.visited_today_count.setText(str(visited_today))
        self.total_patient_count.setText(str(total_patients))

