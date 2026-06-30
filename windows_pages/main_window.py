import sys
import os
import logging
import json
from PyQt6.QtWidgets import QMainWindow, QStackedWidget
from utils.session import Session

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
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
        self.db = db
        self.initialize_auto_session() # 1. Auto-login using config
        self.initialize_pages()        # 2. Skip login page
        
    def initialize_auto_session(self):
        """Loads organization configurations dynamically from AppData."""
        try:
            import os
            import json
            
            app_data_dir = os.path.join(os.environ["LOCALAPPDATA"], "JashThumbAttendance")
            config_path = os.path.join(app_data_dir, 'config.json')

            if not os.path.exists(config_path):
                config_path = "config.json"

            with open(config_path, 'r') as file:
                config_data = json.load(file)
                
            org_id = config_data.get("ORGANIZATION_ID")
            org_name = config_data.get("ORGANIZATION_NAME", "Staff")
            
            from utils.session import Session
            # Start the session automatically
            Session.login(org_id, org_name)
            
        except Exception as e:
            logging.error(f"Configuration Error: Could not load organization variables. {e}", exc_info=True)

    def initialize_pages(self):
        # Directly jump to the core app, skipping login[cite: 5]
        self.show_app_core()

    def show_app_core(self):
        if self.app_core_page is None:
            from windows_pages.app_core_page import AppCorePage
            self.app_core_page = AppCorePage(self.db, self)
            self.main_stack.addWidget(self.app_core_page)

        self.main_stack.setCurrentIndex(self.main_stack.indexOf(self.app_core_page))
        self.app_core_page.refresh_on_login()

    def closeEvent(self, event):
        self.hide()
        from PyQt6.QtWidgets import QApplication
        QApplication.processEvents()

        if self.app_core_page:
            if hasattr(self.app_core_page, "stop_active_scanners"):
                try:
                    self.app_core_page.stop_active_scanners()
                except Exception as e:
                    print(f"Error closing scanner: {e}")
            if hasattr(self.app_core_page, "sync_worker"):
                try:
                    self.app_core_page.sync_worker.stop_worker()
                except Exception as e:
                    print(f"Error stopping sync worker: {e}")
                
        try:
            from utils.session import Session
            if hasattr(Session, 'logout'):
                Session.logout()
        except Exception as e:
            print(f"Session logout error: {e}")
            
        event.accept()