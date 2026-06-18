from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFrame)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from utils.toast_notification import MessageManager

class ForgotPasswordPage(QWidget):

    def __init__(self, db, main_window):
        super().__init__()
        self.db = db
        self.main_window = main_window
        self.setup_ui()

    def setup_ui(self):
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.forgot_card = QFrame()
        self.forgot_card.setFixedSize(500, 600)
        self.forgot_card.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 16px;
            }
        """)
        self.main_layout.addWidget(self.forgot_card)

        self.card_layout = QVBoxLayout()
        self.forgot_card.setLayout(self.card_layout)
        self.card_layout.setContentsMargins(40, 30, 40, 30)
        self.card_layout.setSpacing(10)
        
        self.card_layout.addStretch()

        self.lock_icon = QLabel()
        self.lock_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lock_icon.setStyleSheet("background: transparent;")
        pixmap = QPixmap("assets/password.png")
        pixmap = pixmap.scaled(
            150,
            150,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.lock_icon.setPixmap(pixmap)
        self.card_layout.addWidget(self.lock_icon, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.heading = QLabel("Forgot Password")
        self.heading.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.heading.setStyleSheet("""
            QLabel{
                font-size: 30px;
                font-weight: bold;
                color: #1E293B;
                background: transparent;
            }
        """)
        self.card_layout.addWidget(self.heading)

        self.description = QLabel("Enter your Email to continue.")
        self.description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.description.setStyleSheet("""
            QLabel{
                color: #64748B;
                font-size: 14px;
                background: transparent;
            }
        """)
        self.card_layout.addWidget(self.description)

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

        self.continue_button = QPushButton("CONTINUE")
        self.continue_button.setFixedHeight(55)
        self.continue_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.continue_button.clicked.connect(self.validate_username)
        self.continue_button.setStyleSheet("""
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
        self.card_layout.addWidget(self.continue_button)

        self.back_button = QPushButton("← Back To Login")
        self.back_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.back_button.setStyleSheet("""
            QPushButton{
                border: none;
                background: transparent;
                color: #5C62D6;
                font-size: 13px;
                text-align: left;
            }
            QPushButton:hover{
                color: #4348AB;
                text-decoration: underline;
            }
        """)
        self.back_button.clicked.connect(self.open_login_window)
        self.card_layout.addWidget(self.back_button)

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

    def open_login_window(self):
        self.main_window.show_login_page()

    def validate_username(self):
        username = self.username_input.text().strip()

        if not username:
            MessageManager.show_message(
                self.message_label,
                "Please enter Email.",
                "warning"
            )
            return

        organization = self.db.organizations.find_one({
            "email": username
        })

        if organization is None:
            MessageManager.show_message(
                self.message_label,
                "Email not found.",
                "error"
            )
            return

        MessageManager.show_message(
            self.message_label,
            "Organization found.",
            "success"
        )