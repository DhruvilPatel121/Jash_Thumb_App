from PyQt6.QtWidgets import QMainWindow, QStackedWidget
from windows_pages.auth_pages.login_window import LoginPage
from windows_pages.auth_pages.forgot_password_window import ForgotPasswordPage

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Fingerprint Attendance System")
        self.setMinimumSize(1200, 800)
        self.showMaximized()
        self.setStyleSheet("background-color: #F8FAFC;")
        
        self.db = None
        self.main_stack = QStackedWidget()
        self.setCentralWidget(self.main_stack)
        self.app_core_page = None
        
    def set_database(self, db):
        self.db = db
        self.initialize_pages()
        
    def initialize_pages(self):
        self.login_page = LoginPage(self.db, self)
        self.main_stack.addWidget(self.login_page)
        
        self.forgot_page = ForgotPasswordPage(self.db, self)
        self.main_stack.addWidget(self.forgot_page)
            
        self.main_stack.setCurrentIndex(0)
        
    def show_login_page(self):
        self.main_stack.setCurrentIndex(0)
        
    def show_forgot_page(self):
        self.main_stack.setCurrentIndex(1)
        
    def show_app_core(self):
        if self.app_core_page is None:
            from windows_pages.app_core_page import AppCorePage
            self.app_core_page = AppCorePage(self.db, self)
            self.main_stack.addWidget(self.app_core_page)

        self.main_stack.setCurrentIndex(self.main_stack.indexOf(self.app_core_page))
        self.app_core_page.refresh_on_login()