
from PyQt6.QtWidgets import (QWidget,QLineEdit,QHBoxLayout,QSizePolicy,QPushButton,QFrame, QLabel, QTableWidget, QTableWidgetItem,QHeaderView,QAbstractItemView,QDialog, QVBoxLayout, QCalendarWidget,QScrollArea,QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt, QTimer, QDateTime,QDate,pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtGui import QColor
from utils.delete_attendance_dialog import DeleteAttendanceDialog
from database.organization_repository import OrganizationRepository
from utils.toast_notification import (ToastNotification,PatientSuccessModal)
from database.attendance_worker import (AttendanceWorker)
from datetime import datetime
from utils.manual_attendance_dialog import ManualAttendanceDialog
from utils.session import Session
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtCore import QUrl
import hashlib

class ActionPopup(QWidget):
    def __init__(self, parent_widget, current_state):
        super().__init__()
        self.parent_widget = parent_widget
        self.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.current_role = "Admin"
        self.setup_ui()
        
    def setup_ui(self):
        self.frame = QFrame(self)
        self.frame.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 8px;
            }
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 4)
        self.frame.setGraphicsEffect(shadow)

        layout = QHBoxLayout(self.frame)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(8)

        # 1. Right Button (✅)
        self.right_btn = QPushButton("✅")
        self.right_btn.setFixedSize(35, 35)
        self.right_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.right_btn.setStyleSheet("background-color: #DCFCE7; color: #16A34A; border-radius: 6px; font-size: 16px; border: none;")
        self.right_btn.clicked.connect(lambda: self.select_option('right'))

        # 2. Wrong Button (❌)
        self.wrong_btn = QPushButton("❌")
        self.wrong_btn.setFixedSize(35, 35)
        self.wrong_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.wrong_btn.setStyleSheet("background-color: #FEE2E2; color: #DC2626; border-radius: 6px; font-size: 16px; border: none;")
        self.wrong_btn.clicked.connect(lambda: self.select_option('wrong'))

        # 3. Reset Button (🔄)
        self.reset_btn = QPushButton("🔄")
        self.reset_btn.setFixedSize(35, 35)
        self.reset_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.reset_btn.setStyleSheet("background-color: #F1F5F9; color: #64748B; border-radius: 6px; font-size: 16px; border: none;")
        self.reset_btn.clicked.connect(lambda: self.select_option(None))

        layout.addWidget(self.right_btn)
        layout.addWidget(self.wrong_btn)
        layout.addWidget(self.reset_btn)

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10) 
        main_layout.addWidget(self.frame)

    def select_option(self, state):
        self.parent_widget.set_state(state)
        self.close()


class ActionCellWidget(QWidget):
    state_changed = pyqtSignal(object) 
    opened = pyqtSignal(object) 

    def __init__(self, current_state=None):
        super().__init__()
        self.state = current_state
        self.setup_ui()

    def setup_ui(self):
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.main_btn = QPushButton()
        self.main_btn.setFixedSize(35, 35)
        self.main_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.main_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus) 
        self.main_btn.clicked.connect(self.show_options)

        self.layout.addWidget(self.main_btn)
        self.update_ui()

    def show_options(self):
        self.opened.emit(self) 
        self.popup = ActionPopup(self, self.state)
        self.popup.adjustSize()
        btn_pos = self.main_btn.mapToGlobal(self.main_btn.rect().bottomLeft())
        btn_width = self.main_btn.width()
        popup_width = self.popup.width()
        x = btn_pos.x() + (btn_width // 2) - (popup_width // 2)
        y = btn_pos.y() 
        
        self.popup.move(x, y)
        self.popup.show()

    def set_state(self, state):
        self.state = state
        self.update_ui()
        self.state_changed.emit(state)

    def set_editable(self, editable):
        self.main_btn.setEnabled(editable)

        if editable:
            self.main_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        else:
            self.main_btn.setCursor(Qt.CursorShape.ArrowCursor)

    def update_ui(self):
        if self.state == 'right':
            self.main_btn.setText("✅")
            self.main_btn.setStyleSheet("background-color: #DCFCE7; color: #16A34A; border-radius: 6px; font-size: 16px; border: none;")
        elif self.state == 'wrong':
            self.main_btn.setText("❌")
            self.main_btn.setStyleSheet("background-color: #FEE2E2; color: #DC2626; border-radius: 6px; font-size: 16px; border: none;")
        else:
            self.main_btn.setText("⬜")
            self.main_btn.setStyleSheet("background-color: #F1F5F9; color: #94A3B8; border-radius: 6px; font-size: 18px; border: 1px solid #CBD5E1;")

class DashboardPage(QWidget):
    role_changed = pyqtSignal(str)

    def __init__(self, db=None):
        super().__init__()
        self.current_logs = []
        self.active_action_widget = None
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
        self.selected_date = datetime.now().strftime("%Y-%m-%d")

    def setup_ui(self):
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)

        
        self.header_frame = QFrame()
        self.header_frame.setFixedHeight(80)
        self.header_frame.setStyleSheet("background-color: #F8FAFC; border-bottom: 1px solid #E2E8F0;")
        self.header_layout = QHBoxLayout(self.header_frame)
        self.header_layout.setContentsMargins(10, 12, 20, 12)

        # 1. Title
        self.page_title = QLabel("Attendance Dashboard")
        self.page_title.setStyleSheet("color: #1E293B; font-size: 22px; font-weight: bold; border:none;")

        # 2. Search Input
        self.search_input = QLineEdit()
        self.search_input.textChanged.connect(self.search_attendance_logs)
        self.search_input.setPlaceholderText("Search patient...")
        self.search_input.setFixedHeight(40)
        self.search_input.setMinimumWidth(250)
        self.search_input.setMaximumWidth(500)
        self.search_input.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed
        )
        self.search_input.setStyleSheet("""
        QLineEdit{
            background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px;
            padding-left: 15px; font-size: 14px; color: #334155;
        }
        QLineEdit:focus{ border: 2px solid #5C62D6; }
        """)

        # 3. Filter Date Button
        self.filter_date_btn = QPushButton("Filter Date")
        self.filter_date_btn.setFixedHeight(40) 
        self.filter_date_btn.setMinimumWidth(120)
        self.filter_date_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.filter_date_btn.clicked.connect(self.show_calendar_popup) 
        self.filter_date_btn.setStyleSheet("""
        QPushButton{ background-color: #5C62D6; border: none; border-radius: 8px; padding: 0px 15px; font-size: 13px; color: #FFFFFF; font-weight: bold; }
        QPushButton:hover{ background-color: #4A4FB6; }
        """)

        # 4. Reset Filter Button
        self.reset_btn = QPushButton("Today's List")
        self.reset_btn.setFixedHeight(40)
        self.reset_btn.setMinimumWidth(120)
        self.reset_btn.setCursor(Qt.CursorShape.PointingHandCursor) 
        self.reset_btn.clicked.connect(self.reset_filters) 
        self.reset_btn.setStyleSheet("""
        QPushButton{ background-color: #FEE2E2; border: none; border-radius: 8px; padding: 0px 15px; font-size: 13px; color: #DC2626; font-weight: bold; }
        QPushButton:hover{ background-color: #FECACA; }
        """)

        # 5. Scanner Button
        self.scanner_btn = QPushButton("Start Scanner")
        self.scanner_btn.setFixedHeight(40)
        self.scanner_btn.setMinimumWidth(130)
        self.scanner_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.scanner_btn.clicked.connect(self.start_scanner) 
        self.scanner_btn.setStyleSheet("""
        QPushButton{ background-color: #5C62D6; color: white; border: none; border-radius: 8px; font-size: 13px; font-weight: bold; }
        QPushButton:hover{ background-color: #4C51BF; }
        """)   

        # 6. Date, Time, User Labels
        self.header_date_label = QLabel(f"📅 {QDate.currentDate().toString('dd MMM yyyy')}")
        self.header_date_label.setStyleSheet("color: #64748B; font-size: 15px; font-weight: 600; border:none;")

        self.time_label = QLabel("🕒 03:35 PM")
        self.time_label.setStyleSheet("color: #64748B; font-size: 15px; font-weight: 600; border:none;")

        self.user_label = QLabel("👤 Admin")
        self.user_label.setStyleSheet("color: #64748B; font-size: 15px; font-weight: 600; border:none;")
        self.user_label.setCursor(Qt.CursorShape.PointingHandCursor)
        self.user_label.mousePressEvent = self.show_role_popup
        self.header_layout.addSpacing(80)
        self.header_layout.addWidget(self.page_title)
        self.header_layout.addSpacing(25)
        self.header_layout.addWidget(self.search_input, 1)
        # Buttons
        self.header_layout.addWidget(self.filter_date_btn)
        self.header_layout.addWidget(self.reset_btn)
        self.header_layout.addWidget(self.scanner_btn)
        self.header_layout.addStretch()
        # Right Side
        self.header_layout.addWidget(self.header_date_label)
        self.header_layout.addSpacing(15)
        self.header_layout.addWidget(self.time_label)
        self.header_layout.addSpacing(15)
        self.header_layout.addWidget(self.user_label)
        self.header_layout.addStretch() 
        self.header_layout.addWidget(self.header_date_label)
        self.header_layout.addSpacing(10) 
        self.header_layout.addWidget(self.time_label)
        self.header_layout.addSpacing(10) 
        self.header_layout.addWidget(self.user_label)

        self.main_layout.addWidget(self.header_frame)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setStyleSheet("""
            QScrollArea { border: none; background-color: #F8FAFC; }
            QScrollBar:vertical { border: none; background: transparent; width: 8px; margin: 0px; }
            QScrollBar::handle:vertical { background: #CBD5E1; min-height: 30px; border-radius: 4px; }
            QScrollBar::handle:vertical:hover { background: #94A3B8; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: none; }
        """)

        self.content_area = QFrame()
        self.content_area.setStyleSheet("QFrame{background-color: #F8FAFC;}")
        
        self.scroll_area.setWidget(self.content_area)
        self.main_layout.addWidget(self.scroll_area) 

        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(20, 20, 20, 20) 
        self.content_layout.setSpacing(15)
        self.content_area.setLayout(self.content_layout)

        
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

        
        # Table Formate and Headings
        self.attendance_title = QLabel("Detailed Attendance Logs")
        self.attendance_title.setStyleSheet("""
            QLabel{
                    color: #1E293B;
                    font-size: 20px;
                    font-weight: bold;
                    margin-top: 5px;
                }
            """)
        self.attendance_title.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.manual_attn_btn = QPushButton("Manual Entry")
        self.manual_attn_btn.setFixedHeight(35) 
        self.manual_attn_btn.setMinimumWidth(130)
        self.manual_attn_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.manual_attn_btn.setStyleSheet("""
        QPushButton { 
            background-color: #5C62D6; 
            color: white; 
            border: none; 
            border-radius: 8px; 
            font-size: 13px; 
            font-weight: bold; 
            min-width: 120px;  /* Adjust this so both buttons have the same width */
            min-height: 40px;  /* Adjust this so both buttons have the same height */
        }
        QPushButton:hover { 
            background-color: #4C51BF; 
        }
        """)
        self.manual_attn_btn.clicked.connect(self.open_manual_attendance_dialog)

        attendance_header_layout = QHBoxLayout()
        attendance_header_layout.addWidget(self.attendance_title)
        attendance_header_layout.addStretch() 
        attendance_header_layout.addWidget(self.manual_attn_btn)

        self.content_layout.addLayout(attendance_header_layout)

        self.ortho_frame = QFrame()
        self.ortho_frame.setObjectName("orthoFrame")
        self.ortho_frame.setStyleSheet("""
        QFrame#orthoFrame { 
            background-color: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 16px;
        }
        """)
        
        ortho_layout = QVBoxLayout(self.ortho_frame)
        ortho_layout.setContentsMargins(15, 15, 15, 15)
        ortho_layout.setSpacing(10)

        ortho_title = QLabel("Ortho Department")
        ortho_title.setStyleSheet("""
        QLabel{
            background:#F8FAFC;
            border-radius:8px;
            padding:10px;
            font-size:18px;
            font-weight:700;
            color:#1E293B;
        }
        """)
        
        self.cardio_table = self.create_styled_table() 
        self.cardio_table.setMinimumHeight(600)
        
        ortho_layout.addWidget(ortho_title)
        ortho_layout.addWidget(self.cardio_table)
        self.content_layout.addWidget(self.ortho_frame)
        self.content_layout.addSpacing(20)
        
        # 2. NEURO DEPARTMENT FRAME
        self.neuro_frame = QFrame()
        self.neuro_frame.setObjectName("neuroFrame")
        self.neuro_frame.setStyleSheet("""
        QFrame#neuroFrame { 
            background-color: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 16px;
        }
        """)
        
        neuro_layout = QVBoxLayout(self.neuro_frame)
        neuro_layout.setContentsMargins(15, 15, 15, 15)
        neuro_layout.setSpacing(10)

        neuro_title = QLabel("Neuro Department")
        neuro_title.setStyleSheet("""
        QLabel{
            background:#F8FAFC;
            border-radius:8px;
            padding:10px;
            font-size:18px;
            font-weight:700;
            color:#1E293B;
        }
        """)
        
        self.neuro_table = self.create_styled_table()
        self.neuro_table.setMinimumHeight(600)
        neuro_layout.addWidget(neuro_title)
        neuro_layout.addWidget(self.neuro_table)

        self.content_layout.addWidget(self.neuro_frame)

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

        self.delete_attendance_dialog = DeleteAttendanceDialog(self)
        self.delete_attendance_dialog.attendance_deleted.connect(self.load_today_logs)

    def create_styled_table(self):
        # table = CustomTableWidget()
        table = QTableWidget()
        table.setWordWrap(True)
        table.setColumnCount(9) 
        table.setHorizontalHeaderLabels(["Number", "Patient Name", "Gender", "Age", "Problem", "Check In", " E ", " P ", "Action"])        
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        
        table.setShowGrid(False)
        
        table.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        table.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        table.verticalHeader().setVisible(False)
        table.verticalHeader().setDefaultSectionSize(60)
        table.setWordWrap(True)
        table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        table.setFrameShape(QFrame.Shape.NoFrame)
        
        table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        table.setStyleSheet("""
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
            padding: 10px 7px;
            font-size: 16px;
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

        header = table.horizontalHeader()
        header.setVisible(True)
        header.setHighlightSections(False)
        header.setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setFixedHeight(50) 
        
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch) 
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch) 
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed) 
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.Fixed) 
        header.setSectionResizeMode(8, QHeaderView.ResizeMode.Fixed)

        table.setColumnWidth(0, 90) 
        table.setColumnWidth(2, 80) 
        table.setColumnWidth(3, 70) 
        table.setColumnWidth(5, 120) 
        table.setColumnWidth(6, 90) 
        table.setColumnWidth(7, 90) 
        table.setColumnWidth(8, 90)

        return table
    

    def load_today_logs(self, search_text=None):
        attendance_date = self.selected_date
        organization_id = Session.organization_id
        
        self.current_logs = self.attendance_worker.attendance_repository.get_today_logs(organization_id, attendance_date, search_text)
        self.refresh_tables_from_cache()

    def refresh_tables_from_cache(self):
        neuro_logs = []
        ortho_logs = []

        for record in self.current_logs:
            dept = record.get("department", "").lower().strip() 
            if "neuro" in dept:
                neuro_logs.append(record)
            elif "ortho" in dept:
                ortho_logs.append(record)
        
        # 2. Give Separate Token Numbers for Neuro
        for idx, record in enumerate(neuro_logs):
            record['queue_no'] = idx + 1
            
        for idx, record in enumerate(ortho_logs):
            record['queue_no'] = idx + 1
            
        # 4. Render the tables
        self.render_department_table(self.neuro_table, neuro_logs)
        self.render_department_table(self.cardio_table, ortho_logs)

    def render_department_table(self, target_table, logs):
        target_table.setRowCount(0)

        pending_logs = []
        completed_logs = []

        for record in logs:
            uid = str(record.get("_id", record.get("patient_name", "") + record.get("check_in_time", "")))
            
            state = {
                "consult": record.get("E"),
                "medicine": record.get("P")
            }

            if state['consult'] is not None and state['medicine'] is not None:
                completed_logs.append((record, state, uid))
            else:
                pending_logs.append((record, state, uid))

        final_list = pending_logs + completed_logs

        for row_idx, (record, state, uid) in enumerate(final_list):
            target_table.insertRow(row_idx)
            target_table.setRowHeight(row_idx, 55) 

            is_completed = (state['consult'] is not None and state['medicine'] is not None)
            row_bg_color = QColor("#F8FAFC") if is_completed else QColor("#FFFFFF")

            paid_days = int(record.get("paid_days", 0) or 0)
            used_days = int(record.get("used_days", 0) or 0)
            is_payment_due = used_days > paid_days

            problem = record.get("problem", "").strip()
            if not problem:
                problem = "--"

            check_in_time = record.get("check_in_time", "")

            if check_in_time:
                try:
                    check_in_time = datetime.strptime(
                        check_in_time,
                        "%H:%M:%S"
                    ).strftime("%I:%M:%S %p")
                except ValueError:
                    pass

            items = [
                QTableWidgetItem(""), 
                QTableWidgetItem(record.get("patient_name", "--")),
                QTableWidgetItem(record.get("gender", "--")),
                QTableWidgetItem(str(record.get("age", "--"))),
                QTableWidgetItem(problem),
                QTableWidgetItem(check_in_time),
            ]
            
            for col_index, item in enumerate(items):
                
                if col_index in (1, 4):      # Patient Name and Problem
                    item.setTextAlignment(
                        Qt.AlignmentFlag.AlignLeft |
                        Qt.AlignmentFlag.AlignVCenter
                    )
                else:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item.setBackground(row_bg_color)
                if is_completed:
                    item.setForeground(QColor("#94A3B8")) 
                elif is_payment_due:
                    item.setForeground(QColor("#DC2626"))
                target_table.setItem(row_idx, col_index, item)
            
            queue_no = record.get('queue_no', row_idx + 1)
            badge = QLabel(str(queue_no))
            badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
            badge.setFixedSize(32, 32)

            if is_completed:
                badge.setStyleSheet("""
                QLabel{
                    background-color:#E2E8F0;
                    color:#64748B;
                    border-radius:16px;
                    font-size:14px;
                    font-weight:700;
                }
                """)

            elif is_payment_due:
                badge.setStyleSheet("""
                QLabel{
                    background-color:#FEE2E2;
                    color:#DC2626;
                    border-radius:16px;
                    font-size:14px;
                    font-weight:700;
                }
                """)

            else:
                badge.setStyleSheet("""
                QLabel{
                    background-color:#EEF2FF;
                    color:#4F46E5;
                    border-radius:16px;
                    font-size:14px;
                    font-weight:700;
                }
                """)
            container = QWidget()
            container.setStyleSheet("QWidget{background: transparent;}")
            layout = QHBoxLayout(container)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(badge)           
            target_table.setCellWidget(row_idx, 0, container)
            today = datetime.now().strftime("%Y-%m-%d")
            allow_edit = (self.selected_date == today)
            consult_widget = ActionCellWidget(state['consult'])
            consult_widget.state_changed.connect(
                lambda new_state, attendance_id=record["_id"]:
                self.update_patient_state(
                    attendance_id,
                    "E",
                    new_state
                )
            )
            consult_widget.opened.connect(self.on_action_widget_opened)
            target_table.setCellWidget(row_idx, 6, consult_widget)

            med_widget = ActionCellWidget(state['medicine'])
            med_widget.state_changed.connect(
                lambda new_state, attendance_id=record["_id"]:
                self.update_patient_state(
                    attendance_id,
                    "P",
                    new_state
                )
            )
            med_widget.opened.connect(self.on_action_widget_opened)
            target_table.setCellWidget(row_idx, 7, med_widget)
            consult_widget.setEnabled(allow_edit)
            med_widget.setEnabled(allow_edit)

            delete_btn = QPushButton("🗑️")
            delete_btn.setFixedSize(35, 35)
            
            if (allow_edit or self.selected_date != today) and not is_completed:
                delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
                delete_btn.setStyleSheet("""
                QPushButton{
                    background-color: #FEE2E2;
                    border: none;
                    border-radius: 8px;
                    font-size: 16px;
                    padding: 0px; 
                }
                QPushButton:hover{ background-color: #FECACA; }
                QPushButton:pressed{ border: 1px solid #EF4444; }
                """)
                delete_btn.clicked.connect(lambda _, r=record: self.delete_attendance_dialog.show_dialog(r))
            else:
                delete_btn.setCursor(Qt.CursorShape.ForbiddenCursor)
                delete_btn.setStyleSheet("""
                QPushButton{
                    background-color: #F1F5F9;
                    border: none;
                    border-radius: 8px;
                    font-size: 16px;
                    color: #94A3B8;
                }
                """)
                delete_btn.setEnabled(False)

            # Center the button in the cell
            btn_container = QWidget()
            btn_container.setStyleSheet("QWidget{background: transparent;}")
            btn_layout = QHBoxLayout(btn_container)
            btn_layout.setContentsMargins(0, 0, 0, 0)
            btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            btn_layout.addWidget(delete_btn)
            
            # Add to the 9th column (index 8)
            target_table.setCellWidget(row_idx, 8, btn_container)


    

    def on_action_widget_opened(self, widget):
        try:
            if self.active_action_widget and self.active_action_widget != widget:
                self.active_action_widget.update_ui()
        except RuntimeError:
            self.active_action_widget = None
        self.active_action_widget = widget

    def update_patient_state(self, attendance_id, field_name, new_state):
        today = datetime.now().strftime("%Y-%m-%d")
        if self.selected_date != today:
            return
        
        self.attendance_worker.attendance_repository.update_action_status(
            attendance_id,
            field_name,
            new_state
        )

        self.active_action_widget = None
        self.load_today_logs()

    def load_initial_data(self):
        self.load_today_logs()

    def update_date_time(self):
        current_datetime = QDateTime.currentDateTime()
        current_date = current_datetime.toString("dd MMM yyyy")
        current_time = current_datetime.toString("hh:mm:ss AP")
        self.time_label.setText(f"🕒 {current_time}")
        self.header_date_label.setText(f"📅 {current_date}")

    def on_scanner_connection_failed(self, message):
        ToastNotification.show_toast(
            parent=self, toast_type="error", title="Scanner Not Found", 
            message="Please check the USB connection and try again.", duration=5000 
        )

    def start_scanner(self):
        if not self.scanner_running:
            self.attendance_worker.start_attendance()
        else:
            self.attendance_worker.stop_attendance()

    def on_scanner_connected(self):
        self.scanner_running = True
        self.scanner_btn.setText("Stop Scanner")
        ToastNotification.show_toast(
            parent=self, toast_type="success", title="Scanner Connected",
            message="Device is ready to scan fingerprints.", duration=3000 
        )
        
    def on_scanner_disconnected(self):
        self.scanner_running = False
        self.scanner_btn.setText("Start Scanner")
        ToastNotification.show_toast(
            parent=self, toast_type="warning", title="Scanner Closed",
            message="Attendance Stopped.", duration=3000 
        )

    def stop_scanner_on_page_change(self):
        if self.scanner_running:
            self.attendance_worker.stop_attendance()

    def on_attendance_marked(self, patient):
        PatientSuccessModal.show_modal(
            self,
            serial_no=patient.get('token_no', 'N/A'),
            name=patient.get('name', 'Unknown'),
            age=patient.get('age', 'N/A'),
            gender=patient.get('gender', 'N/A'),
            department=patient.get('department', 'N/A'),
            problem=patient.get('problem', 'N/A'),
            duration=5000
        )
        self.load_today_logs()

    def on_already_taken(self, patient_name):
        ToastNotification.show_toast(
            parent=self, toast_type="warning", title="Entry Already Recorded",
            message=f"{patient_name} has already checked in today.", duration=4000
        )

    def on_patient_not_found(self):
        ToastNotification.show_toast(
            parent=self, toast_type="error", title="Patient Not Found",
            message="This fingerprint is not registered in the system.", duration=4000
        )

    def search_attendance_logs(self):
        search_text = (self.search_input.text().strip())
        self.load_today_logs(search_text)


    def reset_filters(self):
        self.selected_date = datetime.now().strftime("%Y-%m-%d") 
        
        self.search_input.blockSignals(True)
        self.search_input.clear()
        self.search_input.blockSignals(False)
        self.filter_date_btn.setText(" Filter Date")
        
        
        self.load_today_logs()

    def show_calendar_popup(self):
        if self.calendar_popup.isVisible():
            self.calendar_popup.close()
        else:
            button_pos = self.filter_date_btn.mapToGlobal(self.filter_date_btn.rect().bottomRight())
            popup_width = self.calendar_popup.width()
            x_pos = button_pos.x() - popup_width
            y_pos = button_pos.y() + 5
            self.calendar_popup.move(x_pos, y_pos)
            self.calendar_popup.show()

    def on_calendar_date_selected(self, date):
        formatted_date = date.toString('dd MMM yyyy')
        self.filter_date_btn.setText(f"{formatted_date}")
        self.calendar_popup.close()
        
        self.selected_date = date.toString("yyyy-MM-dd")
          
        self.load_today_logs()


    

    def show_role_popup(self, event):
        from utils.role_switch import open_role_switch_popup, open_admin_menu_popup
        
        if getattr(self, 'current_role', 'Admin') == "Staff":
            open_role_switch_popup(self, self.role_changed.emit)
        else:
            self.admin_popup_menu = open_admin_menu_popup(self, self.user_label, self.role_changed.emit)

    def close_all_popups(self):
        if self.calendar_popup.isVisible():
            self.calendar_popup.hide()
        if self.delete_attendance_dialog.isVisible():
            self.delete_attendance_dialog.hide()        
        if self.active_action_widget:
            popup = getattr(self.active_action_widget, "popup", None)
            if popup and popup.isVisible():
                popup.close()
        self.active_action_widget = None

    def on_role_switched(self, role):
        self.role_changed.emit(role)


    def open_manual_attendance_dialog(self):
        dialog = ManualAttendanceDialog(self, self.attendance_worker)
        dialog.exec()