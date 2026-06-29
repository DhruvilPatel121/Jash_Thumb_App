import hashlib
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton,QHBoxLayout
from PyQt6.QtCore import Qt
from database.organization_repository import OrganizationRepository
from utils.session import Session
from utils.toast_notification import ToastNotification

def open_staff_password_dialog(parent):
    dialog = QDialog(parent)
    dialog.setWindowTitle("Change Staff Password")
    dialog.setFixedSize(360, 320)
    
    dialog.setStyleSheet("""
        QDialog { background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 14px; }
        QLabel { color: #0F172A; background: transparent; }
        QLineEdit { background: #FFFFFF; color: #000000; border: 1px solid #CBD5E1; border-radius: 10px; padding: 10px 14px; font-size: 14px; }
        QLineEdit:focus { border: 2px solid #5C62D6; }
        QPushButton { background-color: #5C62D6; color: white; border: none; border-radius: 10px; font-size: 14px; font-weight: 700; padding: 11px; }
        QPushButton:hover { background-color: #4F46E5; }
    """)

    layout = QVBoxLayout(dialog)
    layout.setContentsMargins(20, 18, 20, 18)
    layout.setSpacing(14)

    title = QLabel("Update Staff Password")
    title.setStyleSheet("font-size:18px; font-weight:700; color:#0F172A;")
    layout.addWidget(title)

    def create_pwd_field(placeholder):
        h_layout = QHBoxLayout()
        h_layout.setContentsMargins(0, 0, 0, 0)
        h_layout.setSpacing(8)

        input_field = QLineEdit()
        input_field.setEchoMode(QLineEdit.EchoMode.Password)
        input_field.setPlaceholderText(placeholder)

        t_btn = QPushButton("View") # Initial Text
        t_btn.setFixedSize(65, 42)
        t_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        t_btn.setStyleSheet("""
            QPushButton { 
                background-color: #F8FAFC; 
                border: 1px solid #CBD5E1; 
                border-radius: 10px; 
                font-size: 13px; 
                font-weight: bold;
                color: #3B82F6;
            }
            QPushButton:hover { background-color: #DBEAFE; color: #1D4ED8; }
        """)

        h_layout.addWidget(input_field)
        h_layout.addWidget(t_btn)

        def toggle_view():
            if input_field.echoMode() == QLineEdit.EchoMode.Password:
                input_field.setEchoMode(QLineEdit.EchoMode.Normal)
                t_btn.setText("Mask")
            else:
                input_field.setEchoMode(QLineEdit.EchoMode.Password)
                t_btn.setText("View")

        t_btn.clicked.connect(toggle_view)
        return h_layout, input_field
    
    new_pwd_layout, new_pwd_input = create_pwd_field("Enter New Password...")
    layout.addLayout(new_pwd_layout)

    confirm_pwd_layout, confirm_pwd_input = create_pwd_field("Confirm New Password...")
    layout.addLayout(confirm_pwd_layout)

    # Error Label
    error_label = QLabel("")
    error_label.setMinimumHeight(18)
    error_label.setStyleSheet("color:#DC2626; font-size:12px; font-weight:600;")
    layout.addWidget(error_label)

    # Submit Button
    btn = QPushButton("Update Password")
    btn.setFixedHeight(42)
    btn.setCursor(Qt.CursorShape.PointingHandCursor)
    layout.addWidget(btn)

    # Backend Logic and Validation
    def update_password_logic():
        error_label.setText("")
        new_pwd = new_pwd_input.text().strip()
        confirm_pwd = confirm_pwd_input.text().strip()

        if not new_pwd or not confirm_pwd:
            error_label.setText("Fields cannot be empty.")
            return
        
        if new_pwd != confirm_pwd:
            error_label.setText("Passwords do not match.")
            return

        # Hash new password
        hashed_password = hashlib.sha256(new_pwd.encode("utf-8")).hexdigest()
        
        repository = OrganizationRepository()

        org_data = repository.get_by_id(Session.organization_id)
        if org_data and org_data.get("staff_password") == hashed_password:
            error_label.setText("This password is already registered as your current password.")
            return
        
        # Database call
        success = repository.update_staff_password(Session.organization_id, hashed_password)
        
        if success:
            ToastNotification.show_toast(parent, "success", "Success", "Staff password updated successfully.", 3000)
            dialog.accept() # Close the dialog
        else:
            error_label.setText("Database error. Could not update.")

    btn.clicked.connect(update_password_logic)
    
    # Exec dialog at the end
    dialog.exec()