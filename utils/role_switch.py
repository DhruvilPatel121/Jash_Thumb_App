import hashlib
import logging
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, QWidget, QFrame, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from database.organization_repository import OrganizationRepository
from utils.session import Session
from utils.toast_notification import ToastNotification

logger = logging.getLogger(__name__)

# --- 1. STAFF TO ADMIN PASSWORD DIALOG ---
def open_role_switch_popup(parent, on_success_callback):
    logger.info("Opening role switch popup")
    dialog = QDialog(parent)
    dialog.setWindowTitle("Admin Authentication")
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

    title = QLabel("Admin Authentication")
    title.setStyleSheet("font-size:18px; font-weight:700; color:#0F172A;")
    layout.addWidget(title)

    subtitle = QLabel("Enter Admin password to proceed.")
    subtitle.setStyleSheet("font-size:13px; color:#475569;")
    layout.addWidget(subtitle)

    pwd_layout = QHBoxLayout()
    pwd_layout.setContentsMargins(0, 0, 0, 0)
    pwd_layout.setSpacing(8)

    pwd_input = QLineEdit()
    pwd_input.setEchoMode(QLineEdit.EchoMode.Password)
    pwd_input.setPlaceholderText("Enter Password...")
    pwd_layout.addWidget(pwd_input)

    toggle_btn = QPushButton("👁️")
    toggle_btn.setFixedSize(60, 42) 
    toggle_btn.setStyleSheet("""
        QPushButton { background-color: #F8FAFC; border: 1px solid #CBD5E1; border-radius: 10px; font-size: 13px; font-weight: 600; color: #475569; }
        QPushButton:hover { background-color: #E2E8F0; color: #0F172A; }
    """)

    def toggle_visibility():
        if pwd_input.echoMode() == QLineEdit.EchoMode.Password:
            pwd_input.setEchoMode(QLineEdit.EchoMode.Normal)
            toggle_btn.setText("🚫")
        else:
            pwd_input.setEchoMode(QLineEdit.EchoMode.Password)
            toggle_btn.setText("👁️")

    toggle_btn.clicked.connect(toggle_visibility)
    pwd_layout.addWidget(toggle_btn)  
    layout.addLayout(pwd_layout)
    
    error_label = QLabel("")
    error_label.setMinimumHeight(18)
    error_label.setStyleSheet("color:#DC2626; font-size:12px; font-weight:600;")
    layout.addWidget(error_label)
    
    btn = QPushButton("Switch to Admin")
    btn.setFixedHeight(42)
    btn.setCursor(Qt.CursorShape.PointingHandCursor)
    layout.addWidget(btn)

    def verify_password():
        logger.info("Verifying admin role password")
        error_label.setText("")
        password = pwd_input.text().strip()
        
        if not password:
            logger.warning("Role switch failed: empty password")
            error_label.setText("Please enter a password.")
            return

        hashed_password = hashlib.sha256(password.encode("utf-8")).hexdigest()
        repository = OrganizationRepository()
        is_admin_password = repository.verify_role_password(Session.organization_id, hashed_password)
        
        if is_admin_password:
            logger.info("Role switch to Admin succeeded")
            dialog.accept()
            ToastNotification.show_toast(parent, "success", "Role Switched", "Switched to Admin successfully.", 3000)
            on_success_callback("Admin")
        else:
            logger.warning("Role switch failed: incorrect admin password")
            error_label.setText("Incorrect Admin password.")
            pwd_input.clear()
            pwd_input.setFocus()

    btn.clicked.connect(verify_password)
    pwd_input.returnPressed.connect(verify_password)
    dialog.exec()


# --- 2. ADMIN DROPDOWN MENU (No Password needed to switch back to Staff) ---
class AdminMenuPopup(QWidget):
    def __init__(self, parent_widget, anchor_widget, on_switch):
        super().__init__(parent_widget)
        logger.info("Initializing AdminMenuPopup")
        self.parent_widget = parent_widget
        self.anchor_widget = anchor_widget
        self.on_switch = on_switch
        self.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setup_ui()

    def setup_ui(self):
        logger.info("Setting up AdminMenuPopup UI")
        self.frame = QFrame(self)
        self.frame.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 12px;
            }
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 5)
        self.frame.setGraphicsEffect(shadow)

        layout = QVBoxLayout(self.frame)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)

        btn_style = """
            QPushButton {
                text-align: left;
                padding: 12px 15px;
                background: transparent;
                border: none;
                font-size: 14px;
                font-weight: 600;
                color: #1E293B;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #F1F5F9;
                color: #4F46E5;
            }
        """

        switch_btn = QPushButton("🔄  Switch to Staff")
        switch_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        switch_btn.setStyleSheet(btn_style)
        
        pwd_btn = QPushButton("🔑  Change Password")
        pwd_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        pwd_btn.setStyleSheet(btn_style)

        switch_btn.clicked.connect(self.do_switch)
        pwd_btn.clicked.connect(self.open_pwd_dialog)

        layout.addWidget(switch_btn)
        layout.addWidget(pwd_btn)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.addWidget(self.frame)

    def do_switch(self):
        logger.info("Switching role to Staff")
        self.close()
        ToastNotification.show_toast(self.parent_widget, "success", "Role Switched", "Switched to Staff successfully.", 3000)
        self.on_switch("Staff")

    def open_pwd_dialog(self):
        logger.info("Opening admin password change dialog from AdminMenuPopup")
        self.close()
        from utils.admin_pwd_change import open_admin_password_dialog
        open_admin_password_dialog(self.parent_widget)

def open_admin_menu_popup(parent, anchor, on_switch):
    logger.info("Opening admin menu popup")
    popup = AdminMenuPopup(parent, anchor, on_switch)
    popup.adjustSize()
    pos = anchor.mapToGlobal(anchor.rect().bottomRight())
    popup.move(pos.x() - popup.width() + 15, pos.y() - 5)
    popup.show()
    return popup