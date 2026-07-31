from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QSizePolicy, QFrame, QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QComboBox, QListView, QLineEdit)
from PyQt6.QtCore import Qt, QTimer, QDate, QDateTime, pyqtSignal
from PyQt6.QtGui import QFont, QColor
import logging
from utils.attendance_history_dialog import AttendanceHistoryDialog
from database.attendance_repository import AttendanceRepository
from database.patient_repository import PatientRepository

logger = logging.getLogger(__name__)

class HoverLabel(QLabel):
    clicked = pyqtSignal(str, str, object, int)
   
    def __init__(self, text, patient_id, created_at, fees):
        super().__init__(text)
        self.patient_id = patient_id
        self.patient_name = text
        self.created_at = created_at
        self.fees = fees
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("""
            QLabel {
                color: #334155; 
                background: transparent;
                font-size: 14px;
            }
            QLabel:hover {
                color: #5C62D6;
                text-decoration: underline; 
            }
        """)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.patient_id, self.patient_name, self.created_at, self.fees)


class PaymentReportPage(QWidget):
    role_changed = pyqtSignal(str)

    def __init__(self, db=None):
        super().__init__()
        logger.info("Initializing PaymentReportPage")
        self.db = db
        self.attendance_repository = AttendanceRepository()
        self.patient_repository = PatientRepository()
        self.current_role = "Admin"
        
        self.active_status_filter = None # Initially no button is selected
        
        self.paid_list = []
        self.due_list = []
        self.last_day_list = []
        self.consultancy_list = []

        self.setup_ui()
        
        self.history_dialog = AttendanceHistoryDialog(self.content_area)
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_date_time)
        self.timer.start(1000)

    def setup_ui(self):
        logger.info("Setting up UI for PaymentReportPage")
        # Main Layout
        self.main_layout = QHBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)

        # Content Area
        self.content_area = QFrame()
        self.content_area.setStyleSheet("""
            QFrame{
                background-color: #F8FAFC;
            }
        """)
        self.main_layout.addWidget(self.content_area)

        # Content Layout
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(20, 20, 20, 20)
        self.content_layout.setSpacing(15)
        self.content_area.setLayout(self.content_layout)

        # Header Layout
        self.header_layout = QHBoxLayout()

        self.page_title = QLabel("Reports")
        self.page_title.setStyleSheet("""
            QLabel{
                color: #1E293B; /* Dark Slate text */
                font-size: 32px;
                font-weight: bold;
            }
        """)

        self.date_label = QLabel(f"📅 {QDate.currentDate().toString('dd MMM yyyy')}")
        self.date_label.setStyleSheet("""
        QLabel{
            color: #64748B;
            font-size: 18px;
            font-weight: 600;
        }
        """)

        self.time_label = QLabel("🕒 --:-- --")
        self.time_label.setStyleSheet("""
        QLabel{
            color: #64748B;
            font-size: 18px;
            font-weight: 600;
        }
        """)

        self.user_label = QLabel("👤 Admin")
        self.user_label.setStyleSheet("""
        QLabel{
            color: #64748B;
            font-size: 18px;
            font-weight: 600;
        }
        """)
        self.user_label.setCursor(Qt.CursorShape.PointingHandCursor)
        self.user_label.mousePressEvent = self.show_role_popup
        
        self.header_layout.addSpacing(60)
        self.header_layout.addWidget(self.page_title)
        
        self.header_layout.addStretch()
        
        # Search Bar inside Header
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search patient...")
        self.search_input.setFixedHeight(45)
        self.search_input.setMinimumWidth(350)
        self.search_input.setMaximumWidth(700)
        self.search_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
                
        self.search_input.setStyleSheet("""
        QLineEdit{
            background-color: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 10px;
            padding-left: 15px;
            font-size: 14px;
            color: #334155;
        }
        QLineEdit:focus{ border: 2px solid #5C62D6; }
        """)
        self.header_layout.addWidget(self.search_input)
        self.search_input.textChanged.connect(self.search_patients)
        
        self.header_layout.addStretch()
        self.header_layout.addWidget(self.date_label)
        self.header_layout.addSpacing(20)
        self.header_layout.addWidget(self.time_label)
        self.header_layout.addSpacing(20)
        self.header_layout.addWidget(self.user_label)
        
        self.content_layout.addLayout(self.header_layout)
        self.content_layout.addSpacing(20)
        
        # Filter Layout (Month, Year, and Count Buttons)
        self.filter_layout = QHBoxLayout()
        self.filter_layout.setSpacing(15)
        
        self.month_combo = QComboBox()
        months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
        self.month_combo.addItems(months)
        current_month_index = QDate.currentDate().month() - 1
        self.month_combo.setCurrentIndex(current_month_index)
        
        self.year_combo = QComboBox()
        current_year = QDate.currentDate().year()
        years = [str(y) for y in range(current_year - 3, current_year + 3)]
        self.year_combo.addItems(years)
        self.year_combo.setCurrentText(str(current_year))
        
        # Override native Windows popup by setting a QListView
        self.month_combo.setView(QListView())
        self.month_combo.view().setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.year_combo.setView(QListView())
        self.year_combo.view().setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        combo_style = """
        QComboBox {
            background-color: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 8px;
            padding: 8px 15px;
            font-size: 15px;
            color: #334155;
            font-weight: 500;
            min-width: 120px;
        }
        QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 30px;
            border-left: none;
        }
        QComboBox::down-arrow {
            image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="%2364748B" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"></polyline></svg>');
            width: 16px;
            height: 16px;
            margin-right: 10px;
        }
        QComboBox QAbstractItemView {
            background-color: #FFFFFF;
            border: 1px solid #E2E8F0;
            color: #334155;
            outline: none;
        }
        QComboBox QAbstractItemView::item {
            border: none;
            padding: 4px 10px;
        }
        QComboBox QAbstractItemView::item:selected {
            background-color: #EEF2FF;
            color: #5C62D6;
            border: none;
            outline: none;
        }
        QComboBox QAbstractItemView::item:hover {
            background-color: #F8FAFC;
            border: none;
        }
        """
        self.month_combo.setStyleSheet(combo_style)
        self.year_combo.setStyleSheet(combo_style)
        
        self.month_combo.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.year_combo.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        
        self.month_combo.currentIndexChanged.connect(self.on_filter_changed)
        self.year_combo.currentIndexChanged.connect(self.on_filter_changed)
        
        filter_label = QLabel("Select Period: ")
        filter_label.setStyleSheet("color: #64748B; font-size: 16px; font-weight: bold;")
        
        # Count Buttons
        self.paid_btn = QPushButton("Paid: 0")
        self.last_day_btn = QPushButton("Last Day: 0")
        self.due_btn = QPushButton("Due: 0")
        self.consultancy_btn = QPushButton("Consultancy: 0")
        
        self.total_paid_days_lbl = QLabel("Total Paid Days: 0")
        self.total_used_days_lbl = QLabel("Total Used Days: 0")
        
        summary_style = """
            QLabel {
                background-color: #F1F5F9; border: 1px solid #CBD5E1; border-radius: 8px;
                padding: 8px 15px; color: #334155; font-size: 15px; font-weight: bold;
            }
        """
        self.total_paid_days_lbl.setStyleSheet(summary_style)
        self.total_used_days_lbl.setStyleSheet(summary_style)
        
        self.paid_base_style = """
            QPushButton {
                background-color: #ECFDF5; border: 1px solid #A7F3D0; border-radius: 8px;
                padding: 8px 20px; color: #065F46; font-size: 15px; font-weight: bold;
            }
            QPushButton:hover { border: 2px solid #10B981; }
        """
        self.last_day_base_style = """
            QPushButton {
                background-color: #FFFBEB; border: 1px solid #FDE68A; border-radius: 8px;
                padding: 8px 20px; color: #92400E; font-size: 15px; font-weight: bold;
            }
            QPushButton:hover { border: 2px solid #F59E0B; }
        """
        self.due_base_style = """
            QPushButton {
                background-color: #FEF2F2; border: 1px solid #FECACA; border-radius: 8px;
                padding: 8px 20px; color: #991B1B; font-size: 15px; font-weight: bold;
            }
            QPushButton:hover { border: 2px solid #EF4444; }
        """
        self.consultancy_base_style = """
            QPushButton {
                background-color: #FAF5FF; border: 1px solid #E9D5FF; border-radius: 8px;
                padding: 8px 20px; color: #7E22CE; font-size: 15px; font-weight: bold;
            }
            QPushButton:hover { border: 2px solid #A855F7; }
        """
        
        for btn in [self.paid_btn, self.last_day_btn, self.due_btn, self.consultancy_btn]:
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFixedHeight(40)
            
        self.paid_btn.clicked.connect(lambda: self.set_active_filter("Paid"))
        self.last_day_btn.clicked.connect(lambda: self.set_active_filter("Last Day"))
        self.due_btn.clicked.connect(lambda: self.set_active_filter("Due"))
        self.consultancy_btn.clicked.connect(lambda: self.set_active_filter("Consultancy"))
        
        self.filter_layout.addStretch() # Center align start
        self.filter_layout.addWidget(filter_label)
        self.filter_layout.addWidget(self.month_combo)
        self.filter_layout.addWidget(self.year_combo)
        self.filter_layout.addSpacing(20) # separator between dropdowns and buttons
        self.filter_layout.addWidget(self.paid_btn)
        self.filter_layout.addWidget(self.last_day_btn)
        self.filter_layout.addWidget(self.due_btn)
        self.filter_layout.addWidget(self.consultancy_btn)
        self.filter_layout.addSpacing(20)
        self.filter_layout.addWidget(self.total_paid_days_lbl)
        self.total_paid_days_lbl.hide()  # Hidden: paid_days is lifetime field, not reliable for monthly totals
        self.filter_layout.addWidget(self.total_used_days_lbl)
        self.filter_layout.addStretch() # Center align end
        
        self.content_layout.addLayout(self.filter_layout)
        self.content_layout.addSpacing(20)

        # Table Container
        self.table_frame = QFrame()
        self.table_frame.setStyleSheet("""
        QFrame{
            background-color: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 16px;
        }
        """)
        self.content_layout.addWidget(self.table_frame)

        # Table Layout
        self.table_layout = QVBoxLayout()
        self.table_layout.setContentsMargins(10, 0, 10, 10)
        self.table_frame.setLayout(self.table_layout)

        # Report Table
        self.report_table = QTableWidget()
        self.report_table.setWordWrap(True)
        self.report_table.setColumnCount(10)
        self.report_table.setHorizontalHeaderLabels([
            "Number", "Name", "Age", "Mobile", "Department", 
            "Problem", "Total Paid", "Total Used", "Monthly Visits", "Last Visit Date"
        ])

        self.report_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.report_table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.report_table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.report_table.setShowGrid(False)
        self.report_table.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.report_table.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.report_table.verticalHeader().setVisible(False)
        self.report_table.verticalHeader().setDefaultSectionSize(70)
        self.report_table.setFrameShape(QFrame.Shape.NoFrame)
        self.report_table.horizontalHeader().setHighlightSections(False)
        self.report_table.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)

        self.report_table.setStyleSheet("""
        QTableWidget{
            background-color: #FFFFFF;
            border: none;
            color: #334155;
            font-size: 16px;
        }
        QTableWidget::item{
            padding: 8px;
            border-bottom: 1px solid #EDF2F7;
        }
        QHeaderView::section{
            background-color: #FFFFFF;
            color: #475569;
            border: none;
            padding: 18px 5px;
            font-size: 14px;
            font-weight: 600;
        }
        QScrollBar:vertical{ background: transparent; width: 10px; margin: 0px; border: none; }
        QScrollBar::handle:vertical{ background: #CBD5E1; min-height: 40px; border-radius: 5px; }
        QScrollBar::handle:vertical:hover{ background: #94A3B8; }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical{ height: 0px; }
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical{ background: transparent; }
        QScrollBar:horizontal{ background: transparent; height: 10px; margin: 0px; border: none; }
        QScrollBar::handle:horizontal{ background: #CBD5E1; min-width: 40px; border-radius: 5px; }
        QScrollBar::handle:horizontal:hover{ background: #94A3B8; }
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal{ width: 0px; }
        QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal{ background: transparent; }
        """)

        self.table_layout.addWidget(self.report_table)

        header = self.report_table.horizontalHeader()
        header.setFixedHeight(60)

        self.report_table.setColumnWidth(0, 80)   # Number
        self.report_table.setColumnWidth(2, 70)   # Age
        self.report_table.setColumnWidth(3, 120)  # Mobile
        self.report_table.setColumnWidth(4, 120)  # Department
        self.report_table.setColumnWidth(6, 100)  # Paid Days
        self.report_table.setColumnWidth(7, 100)  # Used Days
        self.report_table.setColumnWidth(8, 120)  # Monthly Visits
        self.report_table.setColumnWidth(9, 150)  # Last Visit Date
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch) # Name stretches
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch) # Problem stretches
        
        # Footer
        self.footer_layout = QHBoxLayout()
        self.footer_layout.setContentsMargins(0, 10, 0, 0)
        self.footer_label = QLabel("Handcraft By Shivvilon Solution")
        self.footer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.footer_label.setCursor(Qt.CursorShape.PointingHandCursor)
        self.footer_label.setStyleSheet("""
        QLabel{
            color: #64748B;
            font-size: 13px;
            font-weight: 500;
        }
        QLabel:hover{
            color: #5C62D6;
            text-decoration: underline;
        }
        """)
        def open_website(event):
            import webbrowser
            webbrowser.open("https://shivvilonsolutions.com/")
            
        self.footer_label.mousePressEvent = open_website
        self.footer_layout.addWidget(self.footer_label)
        self.content_layout.addLayout(self.footer_layout)
        
        self.update_active_button_style()

    def show_role_popup(self, event):
        from utils.role_switch import open_role_switch_popup, open_admin_menu_popup
        if getattr(self, 'current_role', 'Admin') == "Staff":
            open_role_switch_popup(self, self.user_label, self.role_changed.emit)
        else:
            self.admin_popup_menu = open_admin_menu_popup(self, self.user_label, self.role_changed.emit)

    def update_date_time(self):
        current_time = QDateTime.currentDateTime().toString("hh:mm A")
        self.time_label.setText(f"🕒 {current_time}")
        self.date_label.setText(f"📅 {QDate.currentDate().toString('dd MMM yyyy')}")

    def on_filter_changed(self):
        self.load_report_data()

    def set_active_filter(self, filter_name):
        self.active_status_filter = filter_name
        self.update_active_button_style()
        self.populate_table()

    def update_active_button_style(self):
        self.paid_btn.setStyleSheet(self.paid_base_style)
        self.last_day_btn.setStyleSheet(self.last_day_base_style)
        self.due_btn.setStyleSheet(self.due_base_style)
        self.consultancy_btn.setStyleSheet(self.consultancy_base_style)
            
        active_base = """
            QPushButton {
                background-color: %s;
                border: 2px solid %s;
                border-radius: 8px;
                padding: 8px 20px;
                color: #FFFFFF;
                font-size: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                border: 2px solid %s;
            }
        """
        if self.active_status_filter == "Paid":
            self.paid_btn.setStyleSheet(active_base % ("#34D399", "#10B981", "#059669"))
        elif self.active_status_filter == "Last Day":
            self.last_day_btn.setStyleSheet(active_base % ("#FBBF24", "#F59E0B", "#D97706"))
        elif self.active_status_filter == "Due":
            self.due_btn.setStyleSheet(active_base % ("#F87171", "#EF4444", "#DC2626"))
        elif self.active_status_filter == "Consultancy":
            self.consultancy_btn.setStyleSheet(active_base % ("#C084FC", "#A855F7", "#9333EA"))

    def load_report_data(self):
        from utils.session import Session
        
        # When opening/refreshing page, ensure 'Paid' is selected by default
        self.active_status_filter = "Paid"
        self.update_active_button_style()
        self.report_table.setRowCount(0)
        
        month = self.month_combo.currentText()
        year = self.year_combo.currentText()
        org_id = Session.organization_id
        
        
        if not org_id:
            return
            
        self.paid_list, self.last_day_list, self.due_list = self.attendance_repository.get_monthly_payment_status(org_id, month, year)
        self.consultancy_list = self.patient_repository.get_monthly_consultancy_patients(org_id, month, year)
        
        self.paid_btn.setText(f"Paid: {len(self.paid_list)}")
        self.last_day_btn.setText(f"Last Day: {len(self.last_day_list)}")
        self.due_btn.setText(f"Due: {len(self.due_list)}")
        self.consultancy_btn.setText(f"Consultancy: {len(self.consultancy_list)}")
        
        # Monthly counts from all attendance records (not from the grouped latest-per-patient list)
        treatment_visits, paid_visits = self.attendance_repository.get_monthly_attendance_counts(org_id, month, year)
        self.total_paid_days_lbl.setText(f"Paid Visits: {paid_visits}")
        self.total_used_days_lbl.setText(f"Total Treatment Days: {treatment_visits}")
        
        self.populate_table()

    def populate_table(self):
        self.report_table.setRowCount(0)
        active_list = []
        active_color = "#334155" # Default text color
        active_bg_color = "#F1F5F9"
        
        if self.active_status_filter == "Paid":
            active_list = self.paid_list
            active_color = "#10B981"
            active_bg_color = "#D1FAE5"
        elif self.active_status_filter == "Last Day":
            active_list = self.last_day_list
            active_color = "#D97706"
            active_bg_color = "#FEF3C7"
        elif self.active_status_filter == "Due":
            active_list = self.due_list
            active_color = "#EF4444"
            active_bg_color = "#FEE2E2"
        elif self.active_status_filter == "Consultancy":
            active_list = self.consultancy_list
            active_color = "#9333EA"
            active_bg_color = "#F3E8FF"
            
        self.report_table.setRowCount(len(active_list))
        
        for row, record in enumerate(active_list):
            
            # Helper to create colored table items
            def create_item(text):
                item = QTableWidgetItem(str(text))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item.setForeground(QColor(active_color))
                return item

            # 1. Number (Circular background)
            number_label = QLabel(str(row + 1))
            number_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            number_label.setFixedSize(30, 30)
            number_label.setStyleSheet(f"""
                QLabel {{
                    background-color: {active_bg_color};
                    color: {active_color};
                    border-radius: 15px;
                    font-size: 14px;
                    font-weight: bold;
                    border: none;
                }}
            """)
            number_container = QWidget()
            number_container.setStyleSheet("background: transparent; border: none;")
            number_layout = QHBoxLayout(number_container)
            number_layout.setContentsMargins(0, 0, 0, 0)
            number_layout.addWidget(number_label, alignment=Qt.AlignmentFlag.AlignCenter)
            self.report_table.setCellWidget(row, 0, number_container)
            
            # 2. Name (HoverLabel or QLabel depending on filter)
            patient_id = str(record.get("patient_id", "")) or str(record.get("_id", ""))
            name = record.get("patient_name") or record.get("name", "")
            created_at = record.get("created_at")
            fees = record.get("payment_per_day", 0)
            
            name_label = HoverLabel(name, patient_id, created_at, fees)
            name_label.clicked.connect(self.open_history)
            name_label.setStyleSheet(f"""
                QLabel {{
                    color: {active_color}; 
                    background: transparent;
                    font-size: 14px;
                    border: none;
                }}
                QLabel:hover {{
                    color: #5C62D6;
                    text-decoration: underline; 
                }}
            """)
            
            name_container = QWidget()
            name_container.setStyleSheet("background-color: transparent; border: none;")
            name_layout = QHBoxLayout(name_container)
            name_layout.setContentsMargins(10, 0, 0, 0)
            name_layout.addWidget(name_label, alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            self.report_table.setCellWidget(row, 1, name_container)
            
            # Age
            self.report_table.setItem(row, 2, create_item(record.get("age", "")))
            
            # Mobile
            self.report_table.setItem(row, 3, create_item(record.get("mobile", "")))
            
            # Department
            self.report_table.setItem(row, 4, create_item(record.get("department", "")))
            
            # Problem
            self.report_table.setItem(row, 5, create_item(record.get("problem", "")))
            
            if self.active_status_filter == "Consultancy":
                # Total Paid, Total Used, Monthly Visits, Last Visit Date
                self.report_table.setItem(row, 6, create_item("--"))
                self.report_table.setItem(row, 7, create_item("--"))
                self.report_table.setItem(row, 8, create_item("--"))
                self.report_table.setItem(row, 9, create_item("--"))
            else:
                # Total Paid
                self.report_table.setItem(row, 6, create_item(record.get("paid_days", 0)))
                
                # Total Used (lifetime)
                self.report_table.setItem(row, 7, create_item(record.get("used_days", 0)))
                
                # Monthly Visits (from new pipeline field)
                self.report_table.setItem(row, 8, create_item(record.get("monthly_visits", 0)))
                
                # Last Visit Date (attendance_date)
                raw_date = str(record.get("attendance_date", ""))
                formatted_date = ""
                if raw_date:
                    qdate = QDate.fromString(raw_date[:10], Qt.DateFormat.ISODate)
                    if qdate.isValid():
                        formatted_date = qdate.toString("dd-MM-yyyy")
                    else:
                        formatted_date = raw_date
                self.report_table.setItem(row, 9, create_item(formatted_date))
        
    def open_history(self, patient_id, patient_name, created_at, fees):
        logger.info("Opening history for patient %s", patient_name)
        from utils.session import Session
        from database.patient_repository import PatientRepository
        
        patient_repo = PatientRepository()
        patient = patient_repo.get_patient_by_id(patient_id)
        consultancy_fees = patient.get("consultancy_fees", 0) if patient else 0
        patient_created_at = patient.get("created_at") if patient else created_at
        
        # Fetch full history for the dialog
        history = self.attendance_repository.get_patient_attendance_history(Session.organization_id, patient_id)
        
        if self.history_dialog:
            self.history_dialog.show_dialog(patient_name, history, patient_created_at, consultancy_fees)

    def search_patients(self, text):
        search_text = text.lower()
        for row in range(self.report_table.rowCount()):
            match = False
            for col in range(self.report_table.columnCount()):
                item = self.report_table.item(row, col)
                if item and search_text in item.text().lower():
                    match = True
                    break
                
                # Check for widgets (like HoverLabel inside QWidget)
                widget = self.report_table.cellWidget(row, col)
                if widget:
                    for child in widget.findChildren(QLabel):
                        if search_text in child.text().lower():
                            match = True
                            break
                    if match:
                        break

            self.report_table.setRowHidden(row, not match)

    def close_all_popups(self):
        if hasattr(self, 'history_dialog') and self.history_dialog and self.history_dialog.isVisible():
            self.history_dialog.close_dialog()
