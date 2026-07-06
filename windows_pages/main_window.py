import sys
import os
import logging
import json
from PyQt6.QtWidgets import QMainWindow, QStackedWidget
from utils.session import Session

logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        logger.info("Initializing MainWindow")
        
        self.setWindowTitle("Fingerprint Attendance System")
        self.setMinimumSize(1280, 720)
        
        # 2. 1366x768 resolution mate specifically resize karo
        self.resize(1600, 900)
        
        self.showMaximized()
        self.setStyleSheet("background-color: #F8FAFC;")
        
        self.db = None
        self.main_stack = QStackedWidget()
        self.setCentralWidget(self.main_stack)
        self.app_core_page = None
        
    def set_database(self, db):
        logger.info("Setting database on MainWindow")
        self.db = db
        self.initialize_auto_session() # 1. Auto-login using config
        self.initialize_pages()        # 2. Skip login page
        
    def initialize_auto_session(self):
        logger.info("Initializing auto session from configuration")
        """Loads organization configurations dynamically from AppData."""
        try:
            import os
            import json
            
            app_data_dir = os.path.join(os.environ["LOCALAPPDATA"], "JashThumbAttendance")
            config_path = os.path.join(app_data_dir, 'config.json')

            if not os.path.exists(config_path):
                logger.warning("Config file not found in AppData, falling back to local config.json")
                config_path = "config.json"

            logger.debug("Loading configuration from: %s", config_path)
            with open(config_path, 'r') as file:
                config_data = json.load(file)
                
            org_id = config_data.get("ORGANIZATION_ID")
            org_name = config_data.get("ORGANIZATION_NAME", "Staff")
            logger.debug("Loaded organization config: ORG_ID=%s ORG_NAME=%s", org_id, org_name)
            
            from utils.session import Session
            # Start the session automatically
            Session.login(org_id, org_name)
            logger.info("Session login called for organization")
            
        except Exception as e:
            logger.error("Configuration Error: Could not load organization variables.", exc_info=True)

    def initialize_pages(self):
        logger.info("Initializing pages in MainWindow")
        # Directly jump to the core app, skipping login[cite: 5]
        self.show_app_core()

    def show_app_core(self):
        logger.info("Showing application core page")
        if self.app_core_page is None:
            logger.debug("App core page not yet created, importing and instantiating AppCorePage")
            from windows_pages.app_core_page import AppCorePage
            self.app_core_page = AppCorePage(self.db, self)
            self.main_stack.addWidget(self.app_core_page)
        else:
            logger.debug("App core page already exists, reusing existing instance")

        self.main_stack.setCurrentIndex(self.main_stack.indexOf(self.app_core_page))
        logger.debug("Set current page index to app core page")
        self.app_core_page.refresh_on_login()
        logger.info("Refreshed app core page after login")

    def closeEvent(self, event):
        logger.info("Handling MainWindow close event")
        self.hide()
        from PyQt6.QtWidgets import QApplication
        QApplication.processEvents()

        if self.app_core_page:
            if hasattr(self.app_core_page, "stop_active_scanners"):
                try:
                    logger.debug("Stopping active scanners on app core page")
                    self.app_core_page.stop_active_scanners()
                except Exception as e:
                    logger.error("Error closing scanner", exc_info=True)
                    print(f"Error closing scanner: {e}")
            if hasattr(self.app_core_page, "sync_worker"):
                try:
                    logger.debug("Stopping sync worker on app core page")
                    self.app_core_page.sync_worker.stop_worker()
                except Exception as e:
                    logger.error("Error stopping sync worker", exc_info=True)
                    print(f"Error stopping sync worker: {e}")
                
        try:
            from utils.session import Session
            if hasattr(Session, 'logout'):
                logger.debug("Logging out session during close event")
                Session.logout()
                logger.info("Session logout completed")
        except Exception as e:
            logger.error("Session logout error", exc_info=True)
            print(f"Session logout error: {e}")
            
        event.accept()
        logger.info("MainWindow close event accepted")