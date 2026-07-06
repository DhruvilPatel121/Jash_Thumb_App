import logging
from PyQt6.QtWidgets import (QVBoxLayout, QLabel, QLineEdit, QPushButton, QWidget, QFrame, QHBoxLayout)
from PyQt6.QtCore import Qt,QTimer
from PyQt6.QtGui import QAction, QIcon, QPixmap
from utils.toast_notification import MessageManager
from utils.session import Session
from database.organization_repository import OrganizationRepository
import hashlib
from utils.resource_path import resource_path
from PyQt6.QtWidgets import QApplication

logger = logging.getLogger(__name__)

class LoginPage(QWidget):
    def __init__(self, db, main_window):
        super().__init__()
        logger.info("Initializing LoginPage")
        self.db = db
        self.main_window = main_window
        self.organization_repository = OrganizationRepository()
        self.setup_ui()

    def setup_ui(self):
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.login_card = QFrame()
        self.login_card.setFixedSize(500, 600) 
        self.login_card.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 16px;
            }
        """)
        self.main_layout.addWidget(self.login_card)

        self.card_layout = QVBoxLayout()
        self.login_card.setLayout(self.card_layout)
        self.card_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.card_layout.setSpacing(8)
        self.card_layout.addStretch()

        self.user_icon = QLabel()
        self.user_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.user_icon.setStyleSheet("background: transparent;")

        pixmap = QPixmap(resource_path("assets/user_2.png"))
        pixmap = pixmap.scaled(120, 120, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.user_icon.setPixmap(pixmap)
        self.card_layout.addWidget(self.user_icon, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.card_layout.setContentsMargins(40, 30, 40, 30)
        self.heading = QLabel("Welcome Back!")
        self.heading.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.heading.setStyleSheet("""
            QLabel{
                font-size: 30px;
                font-weight: bold;
                color: #1E293B;
                background: transparent;
            }
        """)
        self.card_layout.addWidget(self.heading, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Email")
        self.username_input.setFixedHeight(50)
        self.username_input.setStyleSheet("""
            QLineEdit{
                border: 1px solid #E2E8F0;
                border-radius: 8px;
                padding-left: 15px;
                font-size: 16px;
                color: #334155;
                background-color: #FFFFFF;
            }
            QLineEdit:focus{
                border: 2px solid #5C62D6;
            }
        """)
        self.card_layout.addWidget(self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setStyleSheet("""
                QLineEdit{
                    border: 1px solid #E2E8F0;
                    border-radius: 8px;
                    padding-left: 15px;
                    padding-right: 50px;
                    font-size: 16px;
                    color: #334155;
                    background-color: #FFFFFF;
                }
                QLineEdit:focus{
                    border: 2px solid #5C62D6;
                }
        """)
        self.password_input.setFixedHeight(50)
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.returnPressed.connect(self.validate_login)

        self.eye_action = QAction(QIcon(resource_path("assets/eye.png")),"",self)
        self.eye_action.triggered.connect(self.toggle_password_visibility)
        self.password_input.addAction(self.eye_action, QLineEdit.ActionPosition.TrailingPosition)
        self.card_layout.addWidget(self.password_input)
        self.card_layout.addSpacing(20)
        self.login_button = QPushButton("LOGIN")
        self.login_button.setFixedHeight(55)
        self.login_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_button.setStyleSheet("""
            QPushButton{
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #5C62D6, stop:1 #11B1B3);
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover{
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #4A4FB3, stop:1 #0E9294);
            }
            QPushButton:pressed{
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #393D8C, stop:1 #0A7072);
            }
        """)
        self.login_button.clicked.connect(self.validate_login)
        self.card_layout.addWidget(self.login_button)

        self.message_container = QFrame()
        self.message_container.setFixedHeight(50)
        self.message_container.setStyleSheet("background: transparent;")
        self.message_layout = QVBoxLayout()
        self.message_container.setLayout(self.message_layout)
        self.message_label = QLabel(" ")
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.message_layout.addWidget(self.message_label)
        self.card_layout.addWidget(self.message_container)

        self.card_layout.addStretch()
        
    def showEvent(self, event):
        super().showEvent(event)
        logger.debug("LoginPage showEvent triggered")
        QTimer.singleShot(0, self.username_input.setFocus)

    def toggle_password_visibility(self):
        logger.debug("Toggling password visibility in LoginPage")
        if self.password_input.echoMode() == QLineEdit.EchoMode.Password:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.eye_action.setIcon(QIcon(resource_path("assets/eye_off.png")))
        else:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.eye_action.setIcon(QIcon(resource_path("assets/eye.png")))

    def reset_login_state(self):
        logger.debug("Resetting login state in LoginPage")
        self.username_input.setEnabled(True)
        self.password_input.setEnabled(True)
        self.login_button.setText("LOGIN")
        self.login_button.setEnabled(True)

    def validate_login(self):
        username = self.username_input.text().strip()
        raw_password = self.password_input.text().strip()
        logger.info("Validating login for username: %s", username)

        if not username and not raw_password:
            logger.warning("Login validation failed: missing email and password")
            MessageManager.show_message(self.message_label, "Please enter Email and password.", "warning")
            return

        if not username:
            logger.warning("Login validation failed: missing email")
            MessageManager.show_message(self.message_label, "Please enter Email.", "warning")
            return

        if not raw_password:
            logger.warning("Login validation failed: missing password")
            MessageManager.show_message(self.message_label, "Please enter password.", "warning")
            return
        self.login_button.setText("LOGGING IN...")
        self.login_button.setEnabled(False)
        self.username_input.setEnabled(False)
        self.password_input.setEnabled(False)
        QApplication.processEvents()
        hashed_password = hashlib.sha256(raw_password.encode('utf-8')).hexdigest()
        organization = self.organization_repository.verify_login(username, hashed_password)
        
        if organization:
            if organization.get("is_locked", False) == True:
                logger.warning("Login attempt blocked: account locked for %s", username)
                self.reset_login_state()
                MessageManager.show_message(
                    self.message_label, 
                    "Account is locked! Please contact Admin.", 
                    "error"
                )
                return
            Session.login(organization["_id"], organization["email"])
            logger.info("Login successful for %s", username)
            self.main_window.show_app_core()
        else:
            logger.warning("Login failed for %s", username)
            self.reset_login_state()
            MessageManager.show_message(self.message_label, "Invalid Email or password.", "error")