from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QListWidget, 
                             QListWidgetItem, QPushButton, QLineEdit)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCursor
from datetime import datetime
from utils.session import Session

class ManualAttendanceDialog(QDialog):
    def __init__(self, parent, attendance_worker):
        super().__init__(parent)
        self.attendance_worker = attendance_worker
        self.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setup_ui()

    def setup_ui(self):
        # Increased Card Size
        self.setFixedSize(550, 750) 

        main_layout = QVBoxLayout(self)
        # માર્જિન ઓછું કર્યું છે કારણ કે હવે પડછાયા માટે જગ્યા છોડવાની જરૂર નથી
        main_layout.setContentsMargins(0, 0, 0, 0)

        self.bg_frame = QDialog()
        self.bg_frame.setStyleSheet("""
            QDialog { 
                background-color: #FFFFFF; 
                border-radius: 16px; 
                border: 1px solid #E2E8F0;
            }
        """)
        
        bg_layout = QVBoxLayout(self.bg_frame)
        bg_layout.setContentsMargins(30, 30, 30, 25)
        bg_layout.setSpacing(15)

        # 2. Clean Title Section
        title_layout = QVBoxLayout()
        title_layout.setSpacing(5)
        
        title = QLabel("Manual Attendance Entry")
        title.setStyleSheet("font-size: 22px; font-weight: 800; color: #0F172A; background: transparent; border: none;")
        
        subtitle = QLabel("Select a patient to mark today's attendance")
        subtitle.setStyleSheet("font-size: 15px; color: #64748B; background: transparent; border: none;")
        
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        bg_layout.addLayout(title_layout)
        
        bg_layout.addSpacing(10)

        # Search Bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search patient by name...")
        self.search_input.setFixedHeight(45)
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #F8FAFC;
                border: 1px solid #E2E8F0;
                border-radius: 10px;
                padding: 0 15px;
                font-size: 15px;
                color: #1E293B;
            }
            QLineEdit:focus {
                border: 1px solid #818CF8; 
                background-color: #FFFFFF;
            }
        """)
        self.search_input.textChanged.connect(self.filter_patients)
        bg_layout.addWidget(self.search_input)

        # 3. Premium List Widget
        self.list_widget = QListWidget()
        
        # સ્ક્રોલબાર ચાલુ કર્યો છે 
        self.list_widget.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.list_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.list_widget.setStyleSheet("""
            QListWidget { 
                border: none; 
                background-color: transparent;
                outline: none;
            }
            QListWidget::item { 
                padding: 16px 20px; 
                margin-bottom: 10px;
                background-color: #F8FAFC;
                border: 1px solid #E2E8F0;
                border-radius: 10px;
                color: #1E293B; 
                font-size: 15px;
                font-weight: 600;
            }
            QListWidget::item:hover { 
                background-color: #F1F5F9; 
                border: 1px solid #CBD5E1;
                color: #0F172A; 
            }
            QListWidget::item:selected {
                background-color: #EEF2FF;
                border: 1px solid #818CF8;
                color: #3730A3;
            }
            
            /* Custom Scrollbar Styling */
            QScrollBar:vertical {
                background: transparent;
                width: 6px;
                margin: 0px 0px 0px 2px;
                border: none;
            }
            QScrollBar::handle:vertical {
                background: #CBD5E1;
                min-height: 30px;
                border-radius: 3px;
            }
            QScrollBar::handle:vertical:hover {
                background: #94A3B8;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: transparent;
            }
        """)
        bg_layout.addWidget(self.list_widget)

        # 4. Minimalist Footer Button
        self.close_btn = QPushButton("Cancel")
        self.close_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.close_btn.setFixedHeight(45)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                color: #475569;
                border: 1px solid #CBD5E1;
                border-radius: 10px;
                font-size: 15px;
                font-weight: bold;
                margin-top: 5px;
            }
            QPushButton:hover {
                background-color: #F8FAFC;
                color: #0F172A;
                border: 1px solid #94A3B8;
            }
        """)
        self.close_btn.clicked.connect(self.reject)
        bg_layout.addWidget(self.close_btn)

        main_layout.addWidget(self.bg_frame)

        # Load Data
        self.load_patients()
        self.list_widget.itemClicked.connect(self.on_patient_selected)

    def load_patients(self):
        self.list_widget.clear()
        self.search_input.clear() 
        
        organization_id = Session.organization_id
        today_date = datetime.now().strftime("%Y-%m-%d")
        
        all_patients = self.attendance_worker.patient_repository.get_all_by_organization(organization_id)
        
        manual_patients = []
        
        for p in all_patients:
            if p.get("fingerprint_template") == b"MANUAL_BYPASS_DUMMY_TEMPLATE_XYZ":
                already_taken = self.attendance_worker.attendance_repository.is_attendance_taken_today(
                    organization_id, str(p["_id"]), today_date
                )
                
                if not already_taken:
                    manual_patients.append(p)

        if not manual_patients:
            item = QListWidgetItem("All manual attendances are marked for today.")
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setFlags(Qt.ItemFlag.NoItemFlags) 
            self.list_widget.addItem(item)
            self.search_input.hide() 
        else:
            self.search_input.show()
            for p in manual_patients:
                name = p.get('name', 'Unknown')
                mobile = p.get('mobile', 'N/A')
                department = p.get('department', 'N/A')
                
                formatted_text = f"{name}   |   {mobile}   |   {department}"
                
                item = QListWidgetItem(formatted_text)
                item.setData(Qt.ItemDataRole.UserRole, p) 
                self.list_widget.addItem(item)

    def filter_patients(self, search_text):
        search_text = search_text.lower().strip()
        
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            
            if not (item.flags() & Qt.ItemFlag.ItemIsSelectable):
                continue
                
            patient_data = item.data(Qt.ItemDataRole.UserRole)
            if patient_data:
                name = patient_data.get('name', '').lower()
                
                if search_text in name:
                    item.setHidden(False)
                else:
                    item.setHidden(True)

    def on_patient_selected(self, item):
        if item.flags() & Qt.ItemFlag.ItemIsSelectable:
            patient_data = item.data(Qt.ItemDataRole.UserRole)
            self.attendance_worker.process_manual_attendance(patient_data)
            self.accept()