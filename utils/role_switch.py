import hashlib
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton,QHBoxLayout
from PyQt6.QtCore import Qt
from database.organization_repository import OrganizationRepository
from utils.session import Session
from utils.toast_notification import ToastNotification
from utils.staff_pwd_change import open_staff_password_dialog

def open_role_switch_popup(parent, current_role, on_success_callback):
    dialog = QDialog(parent)
    dialog.setWindowTitle("Switch Role")
    
    if current_role == 'Admin':
        dialog.setFixedSize(360, 290)
    else:
        dialog.setFixedSize(360, 250)

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

    title = QLabel("Switch User Role")
    title.setStyleSheet("font-size:18px; font-weight:700; color:#0F172A;")
    layout.addWidget(title)

    subtitle = QLabel("Enter your Admin or Staff password.")
    subtitle.setStyleSheet("font-size:13px; color:#475569;")
    layout.addWidget(subtitle)

    pwd_layout = QHBoxLayout()
    pwd_layout.setContentsMargins(0, 0, 0, 0)
    pwd_layout.setSpacing(8)

    pwd_input = QLineEdit()
    pwd_input.setEchoMode(QLineEdit.EchoMode.Password)
    pwd_input.setPlaceholderText("Enter Password...")
    pwd_layout.addWidget(pwd_input)

    toggle_btn = QPushButton("Show")
    toggle_btn.setFixedSize(60, 42) 
    
    toggle_btn.setStyleSheet("""
        QPushButton { 
            background-color: #F8FAFC; 
            border: 1px solid #CBD5E1; 
            border-radius: 10px; 
            font-size: 13px; 
            font-weight: 600;
            color: #475569;
        }
        QPushButton:hover { background-color: #E2E8F0; color: #0F172A; }
    """)

    def toggle_visibility():
        if pwd_input.echoMode() == QLineEdit.EchoMode.Password:
            pwd_input.setEchoMode(QLineEdit.EchoMode.Normal)
            toggle_btn.setText("Hide")
        else:
            pwd_input.setEchoMode(QLineEdit.EchoMode.Password)
            toggle_btn.setText("Show")

    toggle_btn.clicked.connect(toggle_visibility)
    pwd_layout.addWidget(toggle_btn)  
    layout.addLayout(pwd_layout)
    
    error_label = QLabel("")
    error_label.setMinimumHeight(18)
    error_label.setStyleSheet("color:#DC2626; font-size:12px; font-weight:600;")
    layout.addWidget(error_label)
    
    btn = QPushButton("Switch Role")
    btn.setFixedHeight(42)
    btn.setAutoDefault(False)
    btn.setDefault(False)
    btn.setCursor(Qt.CursorShape.PointingHandCursor)
    layout.addWidget(btn)

    if current_role == 'Admin':
        change_pwd_link = QLabel("Change Staff Password")
        change_pwd_link.setAlignment(Qt.AlignmentFlag.AlignCenter)
        change_pwd_link.setCursor(Qt.CursorShape.PointingHandCursor)
        change_pwd_link.setStyleSheet("""
            QLabel { color: #5C62D6; font-size: 13px; font-weight: 600; margin-top: 5px; }
            QLabel:hover { text-decoration: underline; color: #4F46E5; }
        """)
        
        def open_pwd_dialog(ev):
            dialog.accept() 
            open_staff_password_dialog(parent) 
            
        change_pwd_link.mousePressEvent = open_pwd_dialog
        layout.addWidget(change_pwd_link)

    def verify_password():
        error_label.setText("")
        password = pwd_input.text().strip()
        
        if not password:
            error_label.setText("Please enter a password.")
            return

        hashed_password = hashlib.sha256(password.encode("utf-8")).hexdigest()
        repository = OrganizationRepository()
        role = repository.verify_role_password(Session.organization_id, hashed_password)
        
        if role:
            if role == current_role:
                error_label.setText(f"You are already logged in as {role}.")
                return

            dialog.accept()
            ToastNotification.show_toast(parent, "success", "Role Switched", f"Switched to {role}", 3000)
            
            on_success_callback(role)
        else:
            error_label.setText("Incorrect password. Please try again.")
            pwd_input.clear()
            pwd_input.setFocus()

    btn.clicked.connect(verify_password)
    pwd_input.returnPressed.connect(verify_password)
    dialog.exec()