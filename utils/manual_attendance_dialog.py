from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QListWidget, QListWidgetItem, QPushButton, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QCursor
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
        # 1. Increased Card Size
        self.setFixedSize(480, 550)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)

        self.bg_frame = QDialog()
        self.bg_frame.setStyleSheet("""
            QDialog { 
                background-color: #FFFFFF; 
                border-radius: 16px; 
                border: 1px solid #E2E8F0;
            }
        """)
        
        # Soft Premium Shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(35)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 10)
        self.bg_frame.setGraphicsEffect(shadow)

        bg_layout = QVBoxLayout(self.bg_frame)
        bg_layout.setContentsMargins(30, 30, 30, 25)
        bg_layout.setSpacing(15)

        # 2. Clean Title Section (No Icons)
        title_layout = QVBoxLayout()
        title_layout.setSpacing(5)
        
        title = QLabel("Manual Attendance Entry")
        title.setStyleSheet("font-size: 20px; font-weight: 800; color: #0F172A; background: transparent; border: none;")
        
        subtitle = QLabel("Select a patient to mark today's attendance")
        subtitle.setStyleSheet("font-size: 14px; color: #64748B; background: transparent; border: none;")
        
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        bg_layout.addLayout(title_layout)
        
        bg_layout.addSpacing(5)

        # 3. Premium List Widget
        self.list_widget = QListWidget()
        
        # Hide Scrollbar Completely
        self.list_widget.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
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
        """)
        bg_layout.addWidget(self.list_widget)

        # 4. Minimalist Footer Button
        self.close_btn = QPushButton("Cancel")
        self.close_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.close_btn.setFixedHeight(42)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                color: #475569;
                border: 1px solid #CBD5E1;
                border-radius: 10px;
                font-size: 15px;
                font-weight: bold;
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
        else:
            for p in manual_patients:
                # Clean Format: Name | Mobile | Department (No Icons)
                name = p.get('name', 'Unknown')
                mobile = p.get('mobile', 'N/A')
                department = p.get('department', 'N/A')
                
                formatted_text = f"{name}   |   {mobile}   |   {department}"
                
                item = QListWidgetItem(formatted_text)
                item.setData(Qt.ItemDataRole.UserRole, p) 
                self.list_widget.addItem(item)

    def on_patient_selected(self, item):
        if item.flags() & Qt.ItemFlag.ItemIsSelectable:
            patient_data = item.data(Qt.ItemDataRole.UserRole)
            self.attendance_worker.process_manual_attendance(patient_data)
            self.accept()