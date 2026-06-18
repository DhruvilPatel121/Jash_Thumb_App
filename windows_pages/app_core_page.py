from PyQt6.QtWidgets import QWidget, QHBoxLayout, QStackedWidget
from utils.sidebar import Sidebar 

from windows_pages.pages.dashbord import DashboardPage
from windows_pages.pages.registration_window import RegistrationPage
from windows_pages.pages.patient_window import PatientPage

class AppCorePage(QWidget):
    
    def __init__(self, db, main_window):
        super().__init__()
        self.db = db
        self.main_window = main_window
        self.setup_ui()

    def setup_ui(self):
        self.main_layout = QHBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)

        self.sidebar = Sidebar()
        self.main_layout.addWidget(self.sidebar)

        self.content_stack = QStackedWidget()
        self.main_layout.addWidget(self.content_stack, 1)

        self.dashboard_page = DashboardPage(self.db)
        self.registration_page = RegistrationPage(self.db)
        self.patient_page = PatientPage(self.db)

        self.content_stack.addWidget(self.dashboard_page)      # Index 0
        self.content_stack.addWidget(self.registration_page)   # Index 1
        self.content_stack.addWidget(self.patient_page)        # Index 2

        self.sidebar.dashboard_clicked.connect(self.go_to_dashboard)
        self.sidebar.registration_clicked.connect(self.go_to_registration)
        self.sidebar.patient_clicked.connect(self.go_to_patients)
        self.sidebar.logout_clicked.connect(self.logout_user)
        
        self.sidebar.set_active_page("dashboard")


    def stop_active_scanners(self):
        self.dashboard_page.stop_scanner_on_page_change()
        
        if hasattr(self.registration_page, 'scanner') and self.registration_page.scanner.is_connected():
            self.registration_page.clear_fingerprint_scan()

    def go_to_dashboard(self):
        self.stop_active_scanners()
        self.content_stack.setCurrentIndex(0)
        self.sidebar.set_active_page("dashboard")
        self.dashboard_page.load_initial_data()

    def go_to_registration(self):
        self.stop_active_scanners()
        self.content_stack.setCurrentIndex(1)
        self.sidebar.set_active_page("registration")

    def go_to_patients(self):
        self.stop_active_scanners()
        self.content_stack.setCurrentIndex(2)
        self.sidebar.set_active_page("patient")
        self.patient_page.load_patients()

    def refresh_on_login(self):
        self.go_to_dashboard()

    def logout_user(self):
        self.stop_active_scanners()
        from utils.session import Session
        Session.logout()
        self.main_window.show_login_page()