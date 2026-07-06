from PyQt6.QtCore import QThread
import logging
import time

from database.atlas_connection import AtlasConnection
from sync.sync_manager import SyncManager

logger = logging.getLogger(__name__)

class SyncWorker(QThread):

    def __init__(self):
        super().__init__()
        logger.info("Initializing SyncWorker")
        self.running = False
        self.atlas = AtlasConnection()
        self.sync_manager = SyncManager()

    def start_worker(self):
        self.running = True
        self.start()
        logger.info("Starting SyncWorker and checking Atlas Connection")

    def stop_worker(self):
        self.running = False
        self.wait()
        logger.info("Stopping SyncWorker")

    def run(self):
        while self.running:
            try:
                if self.atlas.is_connected():
                    self.sync_manager.run()
                    # print("Sync completed successfully.")
                else:  
                    logger.warning("Atlas is not connected. Skipping sync.")    
            except Exception as error:
                logger.error("Sync Worker Error", exc_info=True)

            time.sleep(30)