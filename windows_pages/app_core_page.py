from PyQt6.QtWidgets import QWidget, QVBoxLayout, QStackedWidget, QPushButton
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, QRect, Qt
import logging
from utils.sidebar import Sidebar 
from sync.sync_worker import SyncWorker
from windows_pages.pages.dashbord import DashboardPage
from windows_pages.pages.registration_window import RegistrationPage
from windows_pages.pages.patient_window import PatientPage
from utils.license_manager import LicenseManager
from utils.session import Session

logger = logging.getLogger(__name__)

class AppCorePage(QWidget):
    
    def __init__(self, db, main_window):
        super().__init__()
        logger.info("Initializing AppCorePage")
        self.db = db
        self.main_window = main_window
        self.license_manager = LicenseManager()
        self.sidebar_open = False
        self.setup_ui()
        
        
    def setup_ui(self):
        logger.info("Setting up UI for AppCorePage")
        # print("Setting up UI in AppCorePage open")
        self.sync_worker = SyncWorker()
        self.sync_worker.start_worker()
        logger.debug("SyncWorker started in AppCorePage")
        # print("Sync Worker started in AppCorePage")
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)

        self.content_stack = QStackedWidget()
        self.main_layout.addWidget(self.content_stack)
        logger.debug("Content stack added to main layout")
        is_valid = self.license_manager.check_license_validity(
            Session.organization_id,
            self
        )
        logger.debug("License validity check returned: %s", is_valid)

        if not is_valid:
            logger.warning("License invalid or expired, showing LicenseExpiredPage")
            from windows_pages.pages.expiry import LicenseExpiredPage
            self.expired_page = LicenseExpiredPage()
            self.content_stack.addWidget(self.expired_page)
            self.content_stack.setCurrentWidget(self.expired_page)
            logger.info("Expired license page displayed")
            return

        self.dashboard_page = DashboardPage(self.db)
        self.registration_page = RegistrationPage(self.db)
        self.patient_page = PatientPage(self.db)
        logger.debug("Dashboard, Registration, and Patient pages instantiated")

        self.content_stack.addWidget(self.dashboard_page)      # Index 0
        self.content_stack.addWidget(self.registration_page)   # Index 1
        self.content_stack.addWidget(self.patient_page)        # Index 2
        logger.debug("Pages added to content stack")

        self.sidebar = Sidebar(self)
        self.sidebar.hide() 
        logger.debug("Sidebar initialized and hidden")

        self.overlay_btn = QPushButton(self)
        self.overlay_btn.setStyleSheet("background-color: rgba(0, 0, 0, 80); border: none;") 
        self.overlay_btn.hide()
        self.overlay_btn.clicked.connect(self.close_sidebar_from_overlay)
        logger.debug("Overlay button created and connected")

        self.toggle_btn = QPushButton("☰", self)
        self.toggle_btn.setFixedSize(45, 45)
        self.toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.toggle_btn.setStyleSheet("""
            QPushButton {
                background-color: #5C62D6;
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 22px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4C51BF;
            }
        """)
        self.toggle_btn.clicked.connect(self.toggle_sidebar)
        logger.debug("Toggle button created and connected")

        self.registration_page.patient_registered.connect(self.patient_page.refresh_patient_page)
        if hasattr(self.patient_page, 'update_dialog'):
            self.patient_page.update_dialog.patient_updated.connect(self.dashboard_page.load_initial_data)
            logger.debug("Connected patient update dialog signal to dashboard data reload")

        self.sidebar.dashboard_clicked.connect(self.go_to_dashboard)
        self.sidebar.registration_clicked.connect(self.go_to_registration)
        self.sidebar.patient_clicked.connect(self.go_to_patients)
        logger.debug("Sidebar navigation signals connected")
        
        self.dashboard_page.role_changed.connect(self.update_role_access)
        self.registration_page.role_changed.connect(self.update_role_access)
        self.patient_page.role_changed.connect(self.update_role_access)
        logger.debug("Role change signals connected for pages")
        
        self.sidebar.set_active_page("dashboard")
        logger.debug("Sidebar active page set to dashboard")
        
        self.update_role_access("Staff")
        logger.info("AppCorePage UI setup completed")
    
    def update_role_access(self, role):
        logger.info("Updating role access for role: %s", role)
        self.dashboard_page.user_label.setText(f"👤 {role}")
        self.registration_page.user_label.setText(f"👤 {role}")
        self.patient_page.user_label.setText(f"👤 {role}")

        self.dashboard_page.current_role = role
        self.registration_page.current_role = role
        self.patient_page.current_role = role

        if role == "Staff":
            if hasattr(self.sidebar, "patient_btn"):
                self.sidebar.patient_btn.hide()
            
            self.dashboard_page.search_input.hide()
            self.dashboard_page.filter_date_btn.hide()
            self.dashboard_page.reset_btn.hide()
            self.dashboard_page.neuro_table.setColumnHidden(0, True)
            self.dashboard_page.cardio_table.setColumnHidden(0, True)
            logger.debug("Staff role restrictions applied")

            if self.content_stack.currentIndex() == 2:
                self.go_to_dashboard()
        else:
            if hasattr(self.sidebar, "patient_btn"):
                self.sidebar.patient_btn.show()
            self.registration_page.save_btn.setEnabled(True)
            
            self.dashboard_page.search_input.show()
            self.dashboard_page.filter_date_btn.show()
            self.dashboard_page.reset_btn.show()
            self.dashboard_page.neuro_table.setColumnHidden(0, False)
            self.dashboard_page.cardio_table.setColumnHidden(0, False)
            logger.debug("Non-Staff role access applied")
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.toggle_btn.move(20, 20)
        
        self.overlay_btn.setGeometry(0, 0, self.width(), self.height())
        
        if self.sidebar_open:
            self.sidebar.setGeometry(0, 0, 240, self.height())
        else:
            self.sidebar.setGeometry(-240, 0, 240, self.height())
        logger.debug("Resized AppCorePage and positioned sidebar and overlay")
        
    def close_sidebar_from_overlay(self):
        logger.debug("Overlay clicked, attempting to close sidebar if open")
        if self.sidebar_open:
            self.toggle_sidebar()

    def toggle_sidebar(self):
        self.sidebar.show()
        logger.info("Toggling sidebar, currently open: %s", self.sidebar_open)

        start_rect = self.sidebar.geometry()
        if self.sidebar_open:
            end_rect = QRect(-240, 0, 240, self.height())
            self.sidebar_open = False
            self.overlay_btn.hide()
        else:
            end_rect = QRect(0, 0, 240, self.height())
            self.sidebar_open = True
            self.overlay_btn.setGeometry(0, 0, self.width(), self.height())
            self.overlay_btn.show()

        self.overlay_btn.raise_()
        self.sidebar.raise_()
        self.toggle_btn.raise_()

        self.animation = QPropertyAnimation(self.sidebar, b"geometry")
        self.animation.setDuration(250)
        self.animation.setStartValue(start_rect)
        self.animation.setEndValue(end_rect)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        
        if not self.sidebar_open:
            self.animation.finished.connect(self.sidebar.hide)
            
        self.animation.start()
        logger.debug("Sidebar toggle animation started")
    def close_all_page_popups(self):
        logger.debug("Closing all page popups")
        for i in range(self.content_stack.count()):
            page = self.content_stack.widget(i)
            if hasattr(page, "close_all_popups"):
                page.close_all_popups()
                logger.debug("Closed popups for page index %s", i)

    def stop_active_scanners(self):
        logger.info("Stopping active scanners and clearing fingerprint scanners")
        self.dashboard_page.stop_scanner_on_page_change()
        if hasattr(self.registration_page, 'scanner') and self.registration_page.scanner.is_connected():
            self.registration_page.clear_fingerprint_scan()
            logger.debug("Registration page scanner cleared")

    def clear_search_bars(self):
        logger.debug("Clearing search bars on all pages")
        self.dashboard_page.search_input.blockSignals(True)
        self.dashboard_page.search_input.clear()
        self.dashboard_page.search_input.blockSignals(False)
        
        self.patient_page.search_input.blockSignals(True)
        self.patient_page.search_input.clear()
        self.patient_page.search_input.blockSignals(False)
        if hasattr(self.registration_page, 'clear_registration_form'):
            self.registration_page.clear_registration_form()
            logger.debug("Registration form cleared")

    def go_to_dashboard(self):
        logger.info("Navigating to dashboard page")
        if self.sidebar_open:
            self.toggle_sidebar()
        self.close_all_page_popups()
        self.stop_active_scanners()
        self.clear_search_bars()
        
        self.content_stack.setCurrentIndex(0)
        self.sidebar.set_active_page("dashboard")
        self.dashboard_page.load_initial_data()
        logger.debug("Dashboard page activated")

    def go_to_registration(self):
        logger.info("Navigating to registration page")
        if self.sidebar_open:
            self.toggle_sidebar()
        self.close_all_page_popups()
        self.stop_active_scanners()
        self.clear_search_bars()
        self.content_stack.setCurrentIndex(1)
        self.sidebar.set_active_page("registration")
        logger.debug("Registration page activated")

    def go_to_patients(self):
        logger.info("Navigating to patient page")
        if self.sidebar_open:
            self.toggle_sidebar()
        self.close_all_page_popups()
        self.stop_active_scanners()
        self.clear_search_bars()
        self.content_stack.setCurrentIndex(2)
        self.sidebar.set_active_page("patient")
        self.patient_page.load_patients()
        self.patient_page.load_patient_counts()
        logger.debug("Patient page activated and data loads triggered")

    def refresh_on_login(self):
        logger.info("Refreshing AppCorePage on login")
        self.sidebar_open = False
        self.sidebar.setGeometry(-240, 0, 240, self.height())
        self.sidebar.hide()
        self.overlay_btn.hide() 
        self.go_to_dashboard()

