from PyQt6.QtWidgets import QFrame, QVBoxLayout, QPushButton
from PyQt6.QtCore import pyqtSignal, QSize
from PyQt6.QtGui import QIcon


class Sidebar(QFrame):
    dashboard_clicked = pyqtSignal()
    registration_clicked = pyqtSignal()
    patient_clicked = pyqtSignal()
    logout_clicked = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        self.setFixedWidth(220)
        self.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-right: 2px solid #C2C2C2;
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(15, 20, 15, 20)
        layout.setSpacing(10)
        self.setLayout(layout)

        self.dashboard_btn = QPushButton("Dashboard")
        self.dashboard_btn.setIcon(QIcon("assets/dashboard.png"))
        self.dashboard_btn.setIconSize(QSize(24, 24))

        self.registration_btn = QPushButton("Registration")
        self.registration_btn.setIcon(QIcon("assets/registation.png"))
        self.registration_btn.setIconSize(QSize(24, 24))

        self.patient_btn = QPushButton("Patient")
        self.patient_btn.setIcon(QIcon("assets/list.png"))
        self.patient_btn.setIconSize(QSize(24, 24))

        self.logout_btn = QPushButton("Logout")

        # Normal Button Style
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

        # Active Button Style
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

        # Logout Style
        logout_style = """
            QPushButton{
                background-color: #FEF2F2;
                color: #DC2626;
                border: 1px solid #FECACA;
                border-radius: 10px;
                text-align: left;
                padding: 12px 16px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover{
                background-color: #FEE2E2;
                border: 1px solid #FCA5A5;
            }
            QPushButton:pressed{
                background-color: #FECACA;
            }
        """

        # Apply Normal Style
        for btn in [self.dashboard_btn, self.registration_btn, self.patient_btn]:
            btn.setStyleSheet(self.normal_style)

        self.logout_btn.setStyleSheet(logout_style)

        layout.addWidget(self.dashboard_btn)
        layout.addWidget(self.registration_btn)
        layout.addWidget(self.patient_btn)
        layout.addStretch()
        layout.addWidget(self.logout_btn)

        # Signals
        self.dashboard_btn.clicked.connect(self.dashboard_clicked.emit)
        self.registration_btn.clicked.connect(self.registration_clicked.emit)
        self.patient_btn.clicked.connect(self.patient_clicked.emit)
        self.logout_btn.clicked.connect(self.logout_clicked.emit)

    def set_active_page(self, page_name):
        # Reset All Buttons
        self.dashboard_btn.setStyleSheet(self.normal_style)
        self.registration_btn.setStyleSheet(self.normal_style)
        self.patient_btn.setStyleSheet(self.normal_style)

        # Apply Active Style
        if page_name == "dashboard":
            self.dashboard_btn.setStyleSheet(self.active_style)
        elif page_name == "patient":
            self.patient_btn.setStyleSheet(self.active_style)
        elif page_name == "registration":
            self.registration_btn.setStyleSheet(self.active_style)