import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from windows_pages.main_window import MainWindow
import traceback
from PyQt6.QtGui import QIcon
import os
import logging

# Set up the directory and path first
log_dir = os.path.join(
    os.environ["LOCALAPPDATA"],
    "JashThumbAttendance"
)

os.makedirs(log_dir, exist_ok=True)
# print(f"Log directory ensured at: {log_dir}")
log_file = os.path.join(
    log_dir,
    "attendance.log"
)

# Unified Logging Configuration to capture ALL levels
logging.basicConfig(
    filename=log_file,
    level=logging.ERROR, # Setting to DEBUG captures DEBUG, INFO, WARNING, ERROR, and CRITICAL
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    filemode="a",        # 'a' appends to the log, so you don't lose history between restarts
    force=True           # Forces this config to override any default PyQt or underlying library loggers
)

# Initialize the logger for this file AFTER the basicConfig
logger = logging.getLogger(__name__)

def resource_path(relative_path):
    logger.debug("Resolving resource path for: %s", relative_path)
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        logger.debug("Using local directory for resource path resolution")
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def exception_hook(exc_type, exc_value, exc_traceback):
    logger.error("Unhandled exception caught by exception_hook", exc_info=True)
    logging.critical(
        "Unhandled Exception Occurred:\n" + 
        "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    )
    sys.__excepthook__(exc_type, exc_value, exc_traceback)

# Hook apply karo
sys.excepthook = exception_hook

def connect_db(window):
    logger.info("Connecting to database")
    try:
        from database.mongodb_connection import MongoDBConnection
        db = MongoDBConnection()
        window.set_database(db)
        logger.debug("Database connection established and set on window")
    except Exception as error:
        logger.error("Database Startup Error", exc_info=True)
        logging.critical(f"Database Startup Error: {error}", exc_info=True)

def main():
    logger.info("Starting main application")
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(resource_path("assets/logo.ico")))
    
    window = MainWindow()
    window.setWindowIcon(QIcon(resource_path("assets/logo.ico")))
    window.show()
    
    QTimer.singleShot(100, lambda: connect_db(window))
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()