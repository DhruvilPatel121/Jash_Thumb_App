from PyQt6.QtWidgets import (QWidget,QHBoxLayout,QVBoxLayout,QPushButton,QFrame,QLabel,QTableWidget,QTableWidgetItem,QHeaderView,QAbstractItemView,QLineEdit,QDialog, QCalendarWidget)
from PyQt6.QtCore import Qt, QTimer, QDateTime, QDate, pyqtSignal
from PyQt6.QtGui import QFont
from utils.update_patient_dialog import UpdatePatientDialog
from utils.delete_patient_dialog import DeletePatientDialog
from database.patient_repository import PatientRepository
from database.attendance_repository import AttendanceRepository
from utils.session import Session
from utils.attendance_history_dialog import AttendanceHistoryDialog
from datetime import datetime
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtCore import QUrl

class HoverLabel(QLabel):
    clicked = pyqtSignal(str, str)
   

    def __init__(self, text, patient_id):
        super().__init__(text)
        self.patient_id = patient_id
        self.patient_name = text
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
            self.clicked.emit(self.patient_id, self.patient_name)


class PatientPage(QWidget):

    role_changed = pyqtSignal(str)

    def __init__(self, db=None):
        super().__init__()
        self.db = db
        self.active_dialog = None
        self.current_role = "Admin"
        self.patient_repository = PatientRepository()
        self.attendance_repository = AttendanceRepository()
        self.setup_ui()
        self.history_dialog = AttendanceHistoryDialog(self.content_area)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_date_time)
        self.timer.start(1000)
        self.selected_date = None
        self.load_patient_counts()

    def setup_ui(self):
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
        self.content_layout.setContentsMargins(10, 10, 10, 10)
        self.content_layout.setSpacing(10)
        self.content_area.setLayout(self.content_layout)

        self.header_layout = QHBoxLayout()
        self.page_title = QLabel("Patient Management")
        self.page_title.setStyleSheet("""
        QLabel{
            color: #1E293B;
            font-size: 28px;
            font-weight: bold;
        }
        """)

        self.header_date_label = QLabel(f"📅 {QDate.currentDate().toString('dd MMM yyyy')}")
        self.header_date_label.setStyleSheet("""
        QLabel{
            color: #64748B;
            font-size: 18px;
            font-weight: 600;
        }
        """)

        self.time_label = QLabel("🕒 03:35 PM")
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
        self.header_layout.addWidget(self.page_title, alignment=Qt.AlignmentFlag.AlignVCenter)

        self.header_layout.addStretch()

        self.cards_layout = QHBoxLayout()
        self.cards_layout.setSpacing(30) 

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
                    border-radius: 12px;
                }}
            """)
            card.setFixedHeight(80) 
            card.setFixedWidth(170)

            layout = QVBoxLayout()
            layout.setContentsMargins(10, 5, 10, 5) 
            layout.setSpacing(0)

            title = QLabel(card_title)
            title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            title.setStyleSheet("""
                QLabel{
                    color: #64748B; 
                    font-size: 14px;
                    font-weight: bold;
                    border: none;
                    background: transparent;
                }
            """)

            count = QLabel(card_value)
            count.setAlignment(Qt.AlignmentFlag.AlignCenter)
            count.setStyleSheet(f"""
                QLabel{{
                    color: {text_color};
                    font-size: 26px;
                    font-weight: bold;
                    border: none;
                    background: transparent;
                }}
            """)
            
            if card_title == "Today's Visit":
                self.visited_today_count = count
                self.visit_title = title
            elif card_title == "Total Patient":
                self.total_patient_count = count

            layout.addWidget(title)
            layout.addWidget(count)
            card.setLayout(layout)
            
            self.cards_layout.addWidget(card) 

        self.header_layout.addLayout(self.cards_layout)
        self.header_layout.addStretch()
        self.header_layout.addWidget(self.header_date_label, alignment=Qt.AlignmentFlag.AlignVCenter) 
        self.header_layout.addSpacing(20)
        self.header_layout.addWidget(self.time_label, alignment=Qt.AlignmentFlag.AlignVCenter)
        self.header_layout.addSpacing(20)
        self.header_layout.addWidget(self.user_label, alignment=Qt.AlignmentFlag.AlignVCenter)
        
        self.content_layout.addLayout(self.header_layout)
        self.content_layout.addSpacing(5)

        self.calendar_popup = QDialog(self)
        self.calendar_popup.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
        self.calendar_popup.setFixedSize(320, 320)
        popup_layout = QVBoxLayout(self.calendar_popup)
        popup_layout.setContentsMargins(0, 0, 0, 0)

        self.calendar = QCalendarWidget(self.calendar_popup)
        self.calendar.setGridVisible(False)
        self.calendar.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)
        safe_font = QFont()
        safe_font.setPointSize(12)
        self.calendar.setFont(safe_font)
        self.calendar.setStyleSheet("""
        QCalendarWidget { background-color: #FFFFFF; }
        QCalendarWidget QWidget#qt_calendar_navigationbar { background-color: #FFFFFF; border-bottom: 1px solid #F1F5F9; min-height: 45px; }
        QCalendarWidget QToolButton { color: #000000; font-size: 15px; font-weight: 700; padding: 5px 10px; border-radius: 6px; }
        QCalendarWidget QToolButton:hover { background-color: #F1F5F9; }
        QCalendarWidget QToolButton::menu-indicator { image: none; }

        /* Previous Month Mate (Left Arrow Symbol) */
        QCalendarWidget QToolButton#qt_calendar_prevmonth { 
            min-width: 35px; 
            min-height: 35px; 
            background-color: transparent;
            border-radius: 8px;
            color: #000000;
            qproperty-icon: none; /* Default icon clear karva mate */
            qproperty-text: "◀";  /* Text symbol */
            font-size: 18px;
            font-weight: bold;
            margin: 5px;
        }

        /* Next Month Mate (Right Arrow Symbol) */
        QCalendarWidget QToolButton#qt_calendar_nextmonth { 
            min-width: 35px; 
            min-height: 35px; 
            background-color: transparent;
            border-radius: 8px;
            color: #000000;
            qproperty-icon: none; /* Default icon clear karva mate */
            qproperty-text: "▶";  /* Text symbol */
            font-size: 18px;
            font-weight: bold;
            margin: 5px;
        }

        QCalendarWidget QToolButton#qt_calendar_prevmonth:hover, 
        QCalendarWidget QToolButton#qt_calendar_nextmonth:hover { background-color: #E2E8F0; }

        QCalendarWidget QMenu { background-color: #FFFFFF; border: 1px solid #E2E8F0; color: #1E293B; font-size: 14px; padding: 5px; }
        QCalendarWidget QMenu::item:selected { background-color: #EEF2FF; color: #5C62D6; border-radius: 4px; }
        QCalendarWidget QSpinBox::up-button, QCalendarWidget QSpinBox::down-button { width: 0px; height: 0px; border: none; }
        QCalendarWidget QSpinBox { background: #FFFFFF; color: #1E293B; selection-background-color: #5C62D6; selection-color: #FFFFFF; font-size: 14px; border: 1px solid #E2E8F0; border-radius: 4px; padding: 2px; }
        QCalendarWidget QAbstractItemView:enabled { background-color: #FFFFFF; color: #334155; selection-background-color: #93C5FD; selection-color: #1E3A8A; font-size: 14px; font-weight: 500; outline: none; }
        QCalendarWidget QAbstractItemView:disabled { color: #CBD5E1; }
        QCalendarWidget QTableView { alternate-background-color: #FFFFFF; border: none; padding: 5px; }
        QCalendarWidget QAbstractItemView::item { border-radius: 6px; margin: 2px; }
        QCalendarWidget QAbstractItemView::item:hover { background-color: #DBEAFE; color: #1D4ED8; border: 1px solid #BFDBFE; }
        """)

        popup_layout.addWidget(self.calendar)
        self.calendar.clicked.connect(self.on_calendar_date_selected)

        self.search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search patient...")
        self.search_input.setFixedHeight(45)
                
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

        self.filter_date_btn = QPushButton(" Filter Date")
        self.filter_date_btn.setFixedHeight(45)
        self.filter_date_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.filter_date_btn.setStyleSheet("""
        QPushButton{
            background-color: #5C62D6;
            border: none;
            border-radius: 10px;
            padding: 0px 15px; 
            font-size: 14px;
            color: #FFFFFF;
            font-weight: bold;
        }
        QPushButton:hover{ 
            background-color: #4A4FB6; 
        }
        QPushButton:pressed{ 
            border: 1px solid #1D4ED8; 
            padding-top: 3px; 
            padding-left: 18px; 
        }
        """)

        self.reset_btn = QPushButton("All Patient")
        self.reset_btn.setFixedHeight(45)
        self.reset_btn.setCursor(Qt.CursorShape.PointingHandCursor) 
        self.reset_btn.setStyleSheet("""
        QPushButton{
            background-color: #FEE2E2; 
            border: none;
            border-radius: 10px;
            padding: 0px 15px; 
            font-size: 14px;
            color: #DC2626; 
            font-weight: bold;
        }
        QPushButton:hover{ 
            background-color: #FECACA; 
        }
        QPushButton:pressed{ 
            border: 1px solid #B91C1C; 
            padding-top: 3px; 
            padding-left: 18px; 
        }
        """)
    
        self.search_layout.addWidget(self.search_input)
        self.search_layout.addWidget(self.filter_date_btn)
        self.search_layout.addWidget(self.reset_btn)
        self.search_input.textChanged.connect(self.search_patients)
        self.filter_date_btn.clicked.connect(self.show_calendar_popup) 
        self.reset_btn.clicked.connect(self.reset_filters)

        self.content_layout.addLayout(self.search_layout)

        self.filter_status_label = QLabel("Showing: All Patients")
        self.filter_status_label.setStyleSheet("""
        QLabel{
            color: #64748B;
            font-size: 14px;
            font-weight: 600;
            margin-bottom: 5px;
        }
        """)
        self.content_layout.addWidget(self.filter_status_label)

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

        # Patient Table
        self.patient_table = QTableWidget()
        self.patient_table.setWordWrap(True)
        self.patient_table.setColumnCount(9)
        self.patient_table.setHorizontalHeaderLabels([
            "Number", "Name", "Mobile", "Age", "Gender", 
            "Department", "Problem", "Created Date", "Actions"
        ])

        self.patient_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.patient_table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.patient_table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.patient_table.setShowGrid(False)
        self.patient_table.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.patient_table.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.patient_table.verticalHeader().setVisible(False)
        self.patient_table.verticalHeader().setDefaultSectionSize(70)
        self.patient_table.setFrameShape(QFrame.Shape.NoFrame)
        self.patient_table.horizontalHeader().setHighlightSections(False)
        self.patient_table.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)

        self.patient_table.setStyleSheet("""
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

        /* VERTICAL SCROLLBAR */
        QScrollBar:vertical{
            background: transparent;
            width: 10px;
            margin: 0px;
            border: none;
        }
        QScrollBar::handle:vertical{
            background: #CBD5E1;
            min-height: 40px;
            border-radius: 5px;
        }
        QScrollBar::handle:vertical:hover{
            background: #94A3B8;
        }
        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical{
            height: 0px;
        }
        QScrollBar::add-page:vertical,
        QScrollBar::sub-page:vertical{
            background: transparent;
        }

        /* HORIZONTAL SCROLLBAR */
        QScrollBar:horizontal{
            background: transparent;
            height: 10px;
            margin: 0px;
            border: none;
        }
        QScrollBar::handle:horizontal{
            background: #CBD5E1;
            min-width: 40px;
            border-radius: 5px;
        }
        QScrollBar::handle:horizontal:hover{
            background: #94A3B8;
        }
        QScrollBar::add-line:horizontal,
        QScrollBar::sub-line:horizontal{
            width: 0px;
        }
        QScrollBar::add-page:horizontal,
        QScrollBar::sub-page:horizontal{
            background: transparent;
        }
        """)

        self.table_layout.addWidget(self.patient_table)

        header = self.patient_table.horizontalHeader()
        header.setFixedHeight(60)

        self.patient_table.setColumnWidth(0, 70)  # Number
        self.patient_table.setColumnWidth(2, 120) # Mobile
        self.patient_table.setColumnWidth(3, 80)  # Age
        self.patient_table.setColumnWidth(4, 80)  # Gender
        self.patient_table.setColumnWidth(5, 120) # Department
        self.patient_table.setColumnWidth(7, 120) # Created Date
        self.patient_table.setColumnWidth(8, 120) # Actions
        
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Stretch)

        self.update_dialog = UpdatePatientDialog(self.content_area)
        self.update_dialog.patient_updated.connect(self.load_patients)
        self.delete_dialog = DeletePatientDialog(self.content_area)
        self.delete_dialog.patient_deleted.connect(self.refresh_patient_page)

        # Footer
        self.footer_layout = QHBoxLayout()
        self.footer_layout.setContentsMargins(0, 10, 0, 0)
        
        self.footer_label = QLabel("Handcraft By Shivvilon Solution")
        self.footer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.footer_label.setCursor(Qt.CursorShape.PointingHandCursor)

        self.footer_label.setStyleSheet("""
            QLabel {
                color: #94A3B8;
                font-size: 13px;
                font-weight: 500;
                letter-spacing: 0.5px;
            }
            QLabel:hover {
                color: #5C62D6; 
                text-decoration: underline;
            }
        """)
        
        def open_website(event):
            QDesktopServices.openUrl(QUrl("https://shivvilonsolutions.com/"))
        self.footer_label.mousePressEvent = open_website

        self.footer_layout.addWidget(self.footer_label)
        self.content_layout.addLayout(self.footer_layout)


    def load_patients(self, search_text=None):
        patients = self.patient_repository.get_patient_data(Session.organization_id,self.selected_date,search_text)

        self.patient_table.setRowCount(len(patients))
        for row, patient in enumerate(patients):
            
            # Helper function for setting cell
            def set_item(col, text):
                item = QTableWidgetItem(str(text))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.patient_table.setItem(row, col, item)

            set_item(0, row + 1)
            patient_name = patient.get("name", "")
            patient_id = str(patient["_id"])
            
            name_label = HoverLabel(patient_name, patient_id)
            name_label.clicked.connect(self.show_patient_history)

            name_container = QWidget()
            name_container.setStyleSheet("""
                QWidget {
                    background-color: transparent;
                    border: none;
                }
            """)
            name_layout = QHBoxLayout(name_container)
            name_layout.setContentsMargins(10, 0, 0, 0)
            name_layout.addWidget(name_label, alignment=Qt.AlignmentFlag.AlignLeft  | Qt.AlignmentFlag.AlignVCenter)
            self.patient_table.setCellWidget(row, 1, name_container)

            set_item(2, patient.get("mobile", ""))
            set_item(3, patient.get("age", ""))
            set_item(4, patient.get("gender", ""))
            set_item(5, patient.get("department", "--"))
            set_item(6, patient.get("problem", ""))

            def set_item(col, text):
                item = QTableWidgetItem(str(text))

                if col in (1, 6):   # Name, Problem
                    item.setTextAlignment(
                        Qt.AlignmentFlag.AlignLeft |
                        Qt.AlignmentFlag.AlignVCenter
                    )
                else:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                self.patient_table.setItem(row, col, item)
            
            problem = patient.get("problem", "")
            if len(problem) > 150:
                self.patient_table.setRowHeight(row, 120)
            elif len(problem) > 100:
                self.patient_table.setRowHeight(row, 100)
            elif len(problem) > 50:
                self.patient_table.setRowHeight(row, 85)
            else:
                self.patient_table.setRowHeight(row, 70)
            set_item(6,problem)
            
            raw_date = str(patient.get("created_at", ""))
            formatted_date = ""
            if raw_date and raw_date != "None":
                try:
                    formatted_date = datetime.strptime(raw_date[:10], "%Y-%m-%d").strftime("%d-%m-%Y")
                except ValueError:
                    formatted_date = raw_date 
            
            set_item(7, formatted_date)

            self.create_action_buttons(row, patient)

    def load_dashboard_counts(self):
        organization_id = (Session.organization_id)
        attendance_date = self.selected_date
        total_patients = (self.attendance_worker.patient_repository.count_patients(organization_id))
        visited_today = (self.attendance_worker.attendance_repository.count_today_attendance(organization_id,attendance_date))
        self.visited_today_count.setText(str(visited_today))
        self.total_patient_count.setText(str(total_patients))

    def create_action_buttons(self, row, patient):
        container = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(8)

        update_btn = QPushButton("✏️")
        delete_btn = QPushButton("🗑️")

        update_btn.setFixedSize(40, 40)
        delete_btn.setFixedSize(40, 40)
        update_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        update_btn.setStyleSheet("""
        QPushButton{
            background-color: #DBEAFE;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            padding: 0px; 
        }
        QPushButton:hover{ 
            background-color: #BFDBFE; 
        }
        QPushButton:pressed{
            border: 1px solid #3B82F6;
            padding-top: 3px;
            padding-left: 3px; 
        }
        """)

        delete_btn.setStyleSheet("""
        QPushButton{
            background-color: #FEE2E2;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            padding: 0px; 
        }
        QPushButton:hover{ 
            background-color: #FECACA; 
        }
        QPushButton:pressed{
            border: 1px solid #EF4444; 
            padding-top: 3px;
            padding-left: 3px;
        }
        """)

        layout.addWidget(update_btn)
        layout.addWidget(delete_btn)
        container.setLayout(layout)

        self.patient_table.setCellWidget(row, 8, container)
        update_btn.clicked.connect(lambda _, p=patient: self.open_update_dialog(p))
        delete_btn.clicked.connect(lambda _, p=patient: self.open_delete_dialog(p))

    def refresh_patient_page(self):
        self.load_patients()
        self.load_patient_counts()

    def search_patients(self):
        search_text = self.search_input.text().strip()
        self.load_patients(search_text)

    def update_date_time(self):
        current_datetime = QDateTime.currentDateTime()
        current_time = current_datetime.toString("hh:mm:ss AP")
        self.time_label.setText(f"🕒 {current_time}")
        current_date = current_datetime.toString("dd MMM yyyy")
        self.header_date_label.setText(f"📅 {current_date}")

    def reset_filters(self):
        self.selected_date = None
        self.search_input.blockSignals(True)
        self.search_input.clear()
        self.search_input.blockSignals(False)
        self.filter_date_btn.setText(" Filter Date")
        self.filter_status_label.setText("Showing: All Patients") 
        self.visit_title.setText("Today's Visit")
        self.load_patients()
        self.load_patient_counts()

    def show_calendar_popup(self):
        if self.calendar_popup.isVisible():
            self.calendar_popup.close()
            self.active_dialog = None 
        else:
            self.close_active_dialog() 
            
            button_pos = self.filter_date_btn.mapToGlobal(self.filter_date_btn.rect().bottomRight())
            popup_width = self.calendar_popup.width()
            x_pos = button_pos.x() - popup_width
            y_pos = button_pos.y() + 5
            self.calendar_popup.move(x_pos, y_pos)
            self.calendar_popup.show()
            
            self.active_dialog = self.calendar_popup 

    def on_calendar_date_selected(self, date):
        formatted_date = date.toString('dd MMM yyyy')
        self.filter_date_btn.setText(f" {formatted_date}")
        self.filter_status_label.setText(f"Showing: Patients from {formatted_date}")
        self.calendar_popup.close()
        self.selected_date = date.toString("yyyy-MM-dd")
        today = datetime.now().strftime("%Y-%m-%d")  
        if self.selected_date == today:
            self.visit_title.setText("Today's Visit")
        else:
            self.visit_title.setText(formatted_date + " Visit")
        self.load_patients()
        self.load_patient_counts()
            
    def on_date_changed(self, date):
        self.selected_date = date.toString("yyyy-MM-dd")
        self.load_patients()
    
    def show_patient_history(self, patient_id, patient_name):
        self.close_active_dialog() 
        
        history = self.attendance_repository.get_patient_attendance_history(
            Session.organization_id,
            patient_id
        )
        self.history_dialog.show_dialog(
            patient_name,
            history
        )
        self.active_dialog = self.history_dialog 

    def show_role_popup(self, event):
        from utils.role_switch import open_role_switch_popup, open_admin_menu_popup
        
        if getattr(self, 'current_role', 'Admin') == "Staff":
            open_role_switch_popup(self, self.role_changed.emit)
        else:
            self.admin_popup_menu = open_admin_menu_popup(self, self.user_label, self.role_changed.emit)

    def load_patient_counts(self):
        organization_id = Session.organization_id
        attendance_date = (
        self.selected_date
            if self.selected_date
            else datetime.now().strftime("%Y-%m-%d")
        )

        total_patients = self.patient_repository.count_patients(
            organization_id
        )

        today_visit = self.attendance_repository.count_today_attendance(
            organization_id,
            attendance_date
        )

        self.total_patient_count.setText(str(total_patients))
        self.visited_today_count.setText(str(today_visit))

    def close_active_dialog(self):
        if self.active_dialog and self.active_dialog.isVisible():
            self.active_dialog.hide()
        self.active_dialog = None

    def open_update_dialog(self, patient):
        self.close_active_dialog()              
        self.update_dialog.show_form(patient)    
        self.active_dialog = self.update_dialog

    def open_delete_dialog(self, patient):
        self.close_active_dialog()
        self.delete_dialog.show_dialog(patient)
        self.active_dialog = self.delete_dialog