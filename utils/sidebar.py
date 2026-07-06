import logging
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QPushButton, QGraphicsDropShadowEffect
from PyQt6.QtCore import pyqtSignal, QSize, Qt, QPropertyAnimation, QRect
from PyQt6.QtGui import QIcon, QColor

# Tamari banaveli resource_path file ahiya import kari chhe
from utils.resource_path import resource_path 

logger = logging.getLogger(__name__)

class Sidebar(QFrame):
    dashboard_clicked = pyqtSignal()
    registration_clicked = pyqtSignal()
    patient_clicked = pyqtSignal()
    
    state_changed = pyqtSignal(bool) 

    def __init__(self, parent=None):
        super().__init__(parent)
        logger.info("Initializing Sidebar")
        self.is_open = False
        self.setup_ui()

    def setup_ui(self):
        logger.info("Setting up UI for Sidebar")
        self.setFixedWidth(240)
        self.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-right: 2px solid #E2E8F0;
            }
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(2, 0)
        self.setGraphicsEffect(shadow)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 80, 20, 20) 
        layout.setSpacing(20)
        self.setLayout(layout)

        self.dashboard_btn = QPushButton("Dashboard")
        self.dashboard_btn.setIcon(QIcon(resource_path("assets/dashboard.png")))
        self.dashboard_btn.setIconSize(QSize(24, 24))

        self.registration_btn = QPushButton("Registration")
        self.registration_btn.setIcon(QIcon(resource_path("assets/registation.png")))
        self.registration_btn.setIconSize(QSize(24, 24))

        self.patient_btn = QPushButton("Patient")
        self.patient_btn.setIcon(QIcon(resource_path("assets/list.png")))
        self.patient_btn.setIconSize(QSize(24, 24))

        self.normal_style = """
            QPushButton {
                background-color: transparent;
                color: #64748B;
                border: none;
                text-align: left;
                font-weight: bold;
                padding: 12px 16px;
                border-radius: 8px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #F8F9FA;
                color: #334155;
            }
        """

        self.active_style = """
            QPushButton{
                background-color: #5C62D6;
                color: white;
                border: none;
                border-radius: 10px;
                text-align: left;
                padding: 12px 16px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover{
                background-color: #4F46E5;
            }
        """

        for btn in [self.dashboard_btn, self.registration_btn, self.patient_btn]:
            btn.setStyleSheet(self.normal_style)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)

        layout.addWidget(self.dashboard_btn)
        layout.addWidget(self.registration_btn)
        layout.addWidget(self.patient_btn)
        layout.addStretch()

        self.dashboard_btn.clicked.connect(lambda: self.menu_clicked("dashboard"))
        self.registration_btn.clicked.connect(lambda: self.menu_clicked("registration"))
        self.patient_btn.clicked.connect(lambda: self.menu_clicked("patient"))

        self.setGeometry(-240, 0, 240, 1000) 

        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(250) 

    def menu_clicked(self, page):
        logger.debug("Sidebar menu_clicked called with page=%s", page)
        self.close_sidebar()
        if page == "dashboard":
            self.dashboard_clicked.emit()
        elif page == "registration":
            self.registration_clicked.emit()
        elif page == "patient":
            self.patient_clicked.emit()

    def toggle_sidebar(self):
        logger.info("Toggling sidebar state from is_open=%s", self.is_open)
        if self.is_open:
            self.close_sidebar()
        else:
            self.open_sidebar()

    def open_sidebar(self):
        logger.info("Opening sidebar")
        parent_height = self.parent().height() if self.parent() else 800
        self.animation.setStartValue(QRect(-240, 0, 240, parent_height))
        self.animation.setEndValue(QRect(0, 0, 240, parent_height))
        self.is_open = True
        self.raise_() 
        self.animation.start()
        self.state_changed.emit(True) 

    def close_sidebar(self):
        logger.info("Closing sidebar")
        parent_height = self.parent().height() if self.parent() else 800
        self.animation.setStartValue(QRect(0, 0, 240, parent_height))
        self.animation.setEndValue(QRect(-240, 0, 240, parent_height))
        self.is_open = False
        self.animation.start()
        self.state_changed.emit(False) 

    def set_active_page(self, page_name):
        logger.debug("Setting active sidebar page=%s", page_name)
        self.dashboard_btn.setStyleSheet(self.normal_style)
        self.registration_btn.setStyleSheet(self.normal_style)
        self.patient_btn.setStyleSheet(self.normal_style)

        if page_name == "dashboard":
            self.dashboard_btn.setStyleSheet(self.active_style)
        elif page_name == "patient":
            self.patient_btn.setStyleSheet(self.active_style)
        elif page_name == "registration":
            self.registration_btn.setStyleSheet(self.active_style)