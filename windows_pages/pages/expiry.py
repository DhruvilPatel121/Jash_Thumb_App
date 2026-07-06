from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QFrame,
    QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont, QColor
import logging

logger = logging.getLogger(__name__)

class LicenseExpiredPage(QWidget):

    def __init__(self):
        super().__init__()
        logger.info("Initializing LicenseExpiredPage")
        self.setup_ui()

    def setup_ui(self):
        logger.info("Setting up UI for LicenseExpiredPage")
        # 1. Main Background
        self.setStyleSheet("""
        QWidget {
            background-color: #F8FAFC;
        }
        """)
        logger.debug("Applied main background stylesheet")

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # --------------------------------------------------
        # Header (same height as Dashboard)
        # --------------------------------------------------
        self.header = QFrame()
        self.header.setFixedHeight(80)
        self.header.setStyleSheet("""
        QFrame {
            background: #FFFFFF;
            border-bottom: 1px solid #E2E8F0;
        }
        """)
        self.main_layout.addWidget(self.header)
        logger.debug("Header frame created and added to layout")

        # --------------------------------------------------
        # Center Area Container
        # --------------------------------------------------
        self.body_container = QWidget()
        self.body_layout = QVBoxLayout(self.body_container)
        # Align the contents (the card) strictly to the center
        self.body_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # --------------------------------------------------
        # The Information Card (Modern UI approach)
        # --------------------------------------------------
        self.card = QFrame()
        self.card.setFixedSize(600, 500)
        self.card.setObjectName("ExpiryCard")
        self.card.setStyleSheet("""
        QFrame#ExpiryCard {
            background-color: #FFFFFF;
            border-radius: 16px;
            border: 1px solid #E2E8F0;

        }
        """)
        logger.debug("Expiry card created with styling")

        # Add a subtle drop shadow to the card for depth
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setColor(QColor(0, 0, 0, 15))
        shadow.setOffset(0, 8)
        self.card.setGraphicsEffect(shadow)
        logger.debug("Drop shadow effect applied to expiry card")

        # Card Layout
        self.card_layout = QVBoxLayout(self.card)
        self.card_layout.setContentsMargins(50, 40, 50, 40)
        self.card_layout.setSpacing(15)
        self.card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 1. Cross Icon
        self.icon = QLabel("✖")
        self.icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon.setStyleSheet("color: #EF4444; font-size: 65px; font-weight: bold; background-color: transparent; border: none;")
        self.card_layout.addWidget(self.icon)
        logger.debug("Added expiry status icon to card")

        # 2. Main Status Heading
        self.status_title = QLabel("License Expired")
        self.status_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_title.setStyleSheet("color: #0F172A; font-size: 32px; font-weight: 800; background-color: transparent; border: none;")
        self.card_layout.addWidget(self.status_title)

        # 3. Premium Over Message
        self.premium_msg = QLabel("Your application premium is over.")
        self.premium_msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.premium_msg.setStyleSheet("color: #DC2626; font-size: 20px; font-weight: 600; background-color: transparent; border: none;")
        self.card_layout.addWidget(self.premium_msg)

        # 4. Today's Date (Dynamic)
        current_date = QDate.currentDate().toString("dd MMMM yyyy")
        self.date_label = QLabel(f"Date: {current_date}")
        self.date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.date_label.setStyleSheet("color: #64748B; font-size: 16px; font-weight: 500; background-color: transparent; border: none;")
        self.card_layout.addWidget(self.date_label)

        # Spacer to separate date from the instructions
        self.card_layout.addSpacing(10)

        # 5. Instructions & Contact Message
        contact_text = (
            "Recharge to continue using the application.<br><br>"
            "Please contact <b>Shivvilon Solution</b> to renew your license."
        )
        self.contact_msg = QLabel(contact_text)
        self.contact_msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contact_msg.setWordWrap(True)
        self.contact_msg.setStyleSheet("""
        QLabel {
            color: #334155;
            font-size: 18px;
            line-height: 1.5;
            border: none;
            background-color: transparent;
        }
        """)
        self.card_layout.addWidget(self.contact_msg)
        logger.debug("Added expiry instructions and contact message")

        # Add the completed card to the center container
        self.body_layout.addWidget(self.card)

        # Add the center container to the main window layout
        self.main_layout.addWidget(self.body_container)
        logger.info("LicenseExpiredPage UI setup completed")