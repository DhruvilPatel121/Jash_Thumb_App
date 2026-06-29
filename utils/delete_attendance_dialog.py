from PyQt6.QtWidgets import (QFrame, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor
from database.attendance_repository import AttendanceRepository
from utils.toast_notification import ToastNotification
from database.mongodb_connection import DatabaseConnectionError

class DeleteAttendanceDialog(QFrame):

    attendance_deleted = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.attendance_repository = AttendanceRepository()
        self.setup_ui()

    def setup_ui(self):
        self.setObjectName("confirmCard")
        self.hide()
        self.setFixedSize(400, 260)

        # PREMIUM MODERN CSS
        self.setStyleSheet("""
        QFrame#confirmCard {
            background-color: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 16px;
        }
        """)

        # Softer, more dispersed shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(40)
        shadow.setOffset(0, 15)
        shadow.setColor(QColor(0, 0, 0, 30))
        self.setGraphicsEffect(shadow)

        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(30, 25, 30, 25)
        card_layout.setSpacing(12)
        self.setLayout(card_layout)

        # 1. Warning/Trash Icon (Top Center)
        icon_layout = QHBoxLayout()
        icon_label = QLabel("🗑️")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet("""
            background-color: #FEF2F2;
            color: #EF4444;
            border-radius: 25px;
            font-size: 24px;
        """)
        icon_label.setFixedSize(50, 50)
        icon_layout.addWidget(icon_label, alignment=Qt.AlignmentFlag.AlignCenter)
        card_layout.addLayout(icon_layout)

        # 2. Title
        title = QLabel("Delete Attendance")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            background-color: transparent;
            font-size: 18px;
            font-weight: 800;
            color: #0F172A;
            border: none;
            margin-top: 5px;
        """)
        card_layout.addWidget(title)

        # 3. Message
        self.delete_message = QLabel()
        self.delete_message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.delete_message.setWordWrap(True)
        self.delete_message.setStyleSheet("""
            background-color: transparent;
            font-size: 14px;
            color: #64748B;
            border: none;
            line-height: 1.4;
        """)
        card_layout.addWidget(self.delete_message)
        
        card_layout.addStretch()

        # 4. Buttons Layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)

        self.cancel_delete_btn = QPushButton("Cancel")
        self.cancel_delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cancel_delete_btn.setStyleSheet("""
        QPushButton {
            background: #FFFFFF;
            color: #475569;
            border: 1px solid #CBD5E1;
            border-radius: 8px;
            padding: 10px;
            font-size: 14px;
            font-weight: 600;
        }
        QPushButton:hover {
            background: #F8FAFC;
            color: #0F172A;
            border: 1px solid #94A3B8;
        }
        """)

        self.confirm_delete_btn = QPushButton("Delete")
        self.confirm_delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.confirm_delete_btn.setStyleSheet("""
        QPushButton {
            background: #EF4444;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 10px;
            font-size: 14px;
            font-weight: 600;
        }
        QPushButton:hover {
            background: #DC2626;
        }
        """)

        self.cancel_delete_btn.clicked.connect(self.cancel_delete)
        self.confirm_delete_btn.clicked.connect(self.confirm_delete)

        button_layout.addWidget(self.cancel_delete_btn)
        button_layout.addWidget(self.confirm_delete_btn)
        card_layout.addLayout(button_layout)

    def show_dialog(self, record):
        self.record_to_delete = record 
        
        self.delete_message.setText(
            f"Are you sure you want to delete?<br>"
            f"<b style='color:#0F172A; font-size:15px;'>{record.get('patient_name', 'Unknown')}</b><br><br>"
            f"<span style='color:#EF4444; font-size:12px;'>This action cannot be undone.</span>"
        )

        parent = self.parent()
        if parent:
            self.move(
                (parent.width() - self.width()) // 2,
                (parent.height() - self.height()) // 2
            )

        self.show()
        self.raise_()

    def cancel_delete(self):
        self.hide()

    def confirm_delete(self):
        # Calls the function we just created in AttendanceRepository
        success = self.attendance_repository.delete_attendance(
            self.record_to_delete["_id"]
        )

        try:
            if success:
                self.hide()
                ToastNotification.show_toast(
                    parent=self.parent(),
                    toast_type="success",
                    title="Attendance Deleted",
                    message="The attendance record has been successfully deleted.",
                    duration=4000
                )
                self.attendance_deleted.emit() # This triggers the dashboard to reload
            else:
                ToastNotification.show_toast(
                    parent=self.parent(),
                    toast_type="error",
                    title="Error",
                    message="Failed to delete attendance.",
                    duration=4000)
                
        except Exception as error:
            ToastNotification.show_toast(
                self,
                "error",
                "Database Error.",
                str(error)
            )