from PyQt6.QtCore import QThread
import logging
import time

from database.atlas_connection import AtlasConnection
from sync.sync_manager import SyncManager


class SyncWorker(QThread):

    def __init__(self):
        super().__init__()
        self.running = False
        self.atlas = AtlasConnection()
        self.sync_manager = SyncManager()

    def start_worker(self):
        self.running = True
        self.start()
        logging.info("Checking Atlas Connection...")

    def stop_worker(self):
        self.running = False
        self.wait()

    def run(self):
        while self.running:
            try:
                if self.atlas.is_connected():
                    self.sync_manager.run()

            except Exception as error:
                logging.error(
                    f"Sync Worker Error: {error}",
                    exc_info=True
                )

            time.sleep(30)