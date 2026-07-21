from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class LicenseExpiredPage(QWidget):

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        self.setStyleSheet("""
        QWidget{
            background-color:#F8FAFC;
        }
        """)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # --------------------------------------------------
        # Header (same height as Dashboard)
        # --------------------------------------------------

        self.header = QFrame()
        self.header.setFixedHeight(80)
        self.header.setStyleSheet("""
        QFrame{
            background:#F8FAFC;
            border-bottom:1px solid #E2E8F0;
        }
        """)

        self.main_layout.addWidget(self.header)

        # --------------------------------------------------
        # Center Area
        # --------------------------------------------------

        self.body = QWidget()
        self.body_layout = QVBoxLayout(self.body)
        self.body_layout.setContentsMargins(40, 40, 40, 40)
        self.body_layout.setSpacing(18)

        self.body_layout.addStretch()

        # Cross Icon
        self.icon = QLabel("✖")
        self.icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon.setStyleSheet("""
        QLabel{
            color:#DC2626;
            border:none;
        }
        """)

        icon_font = QFont()
        icon_font.setPointSize(90)
        icon_font.setBold(True)
        self.icon.setFont(icon_font)

        self.body_layout.addWidget(self.icon)

        # Message
        self.message = QLabel("Recharge to continue using the Application")
        self.message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.message.setWordWrap(True)

        self.message.setStyleSheet("""
        QLabel{
            color:#1E293B;
            font-size:28px;
            font-weight:700;
            border:none;
        }
        """)

        self.body_layout.addWidget(self.message)

        self.body_layout.addStretch()

        self.main_layout.addWidget(self.body)

       