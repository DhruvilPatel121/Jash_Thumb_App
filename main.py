import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from windows_pages.main_window import MainWindow
import logging
import traceback


logging.basicConfig(
    filename="attendance.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
    )

def exception_hook(exc_type, exc_value, exc_traceback):
    logging.critical(
        "Unhandled Exception Occurred:\n" + 
        "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    )
    sys.__excepthook__(exc_type, exc_value, exc_traceback)

# 3. Hook ne apply karo
sys.excepthook = exception_hook

def connect_db(window):
    try:
        from database.mongodb_connection import MongoDBConnection
        db = MongoDBConnection()
        window.set_database(db)
    except Exception as error:
        logging.critical(f"Database Startup Error: {error}",exc_info=True)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    QTimer.singleShot(100, lambda: connect_db(window))
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
