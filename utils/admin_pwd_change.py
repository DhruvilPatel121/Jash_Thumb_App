import hashlib
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt
from database.organization_repository import OrganizationRepository
from utils.session import Session
from utils.toast_notification import ToastNotification

def open_admin_password_dialog(parent):
    dialog = QDialog(parent)
    dialog.setWindowTitle("Change Admin Password")
    dialog.setFixedSize(380, 400)
    
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

    title = QLabel("Update Admin Password")
    title.setStyleSheet("font-size:18px; font-weight:700; color:#0F172A;")
    layout.addWidget(title)

    def create_pwd_field(placeholder):
        h_layout = QHBoxLayout()
        h_layout.setContentsMargins(0, 0, 0, 0)
        h_layout.setSpacing(8)

        input_field = QLineEdit()
        input_field.setEchoMode(QLineEdit.EchoMode.Password)
        input_field.setPlaceholderText(placeholder)

        t_btn = QPushButton("👁️")
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
                t_btn.setText("🚫")
            else:
                input_field.setEchoMode(QLineEdit.EchoMode.Password)
                t_btn.setText("👁️")

        t_btn.clicked.connect(toggle_view)
        return h_layout, input_field
    
    old_pwd_layout, old_pwd_input = create_pwd_field("Enter Old Password...")
    layout.addLayout(old_pwd_layout)

    new_pwd_layout, new_pwd_input = create_pwd_field("Enter New Password...")
    layout.addLayout(new_pwd_layout)

    confirm_pwd_layout, confirm_pwd_input = create_pwd_field("Confirm New Password...")
    layout.addLayout(confirm_pwd_layout)

    # Error Label
    error_label = QLabel("")
    error_label.setMinimumHeight(30)
    error_label.setWordWrap(True)
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
        old_pwd = old_pwd_input.text().strip()
        new_pwd = new_pwd_input.text().strip()
        confirm_pwd = confirm_pwd_input.text().strip()

        if not old_pwd or not new_pwd or not confirm_pwd:
            error_label.setText("All fields are required.")
            return
        
        if new_pwd != confirm_pwd:
            error_label.setText("New passwords do not match.")
            return

        repository = OrganizationRepository()
        org_data = repository.get_by_id(Session.organization_id)
        
        hashed_old = hashlib.sha256(old_pwd.encode("utf-8")).hexdigest()
        
        if org_data.get("password") != hashed_old:
            error_label.setText("Incorrect old password.")
            return

        hashed_new = hashlib.sha256(new_pwd.encode("utf-8")).hexdigest()
        
        if hashed_old == hashed_new:
            error_label.setText("New password cannot be the same as the old password.")
            return
        
        success = repository.update_admin_password(Session.organization_id, hashed_new)
        
        if success:
            ToastNotification.show_toast(parent, "success", "Success", "Admin password updated successfully.", 3000)
            dialog.accept() 
        else:
            error_label.setText("Database error. Could not update.")

    btn.clicked.connect(update_password_logic)
    dialog.exec()