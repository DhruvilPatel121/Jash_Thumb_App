import os
import sys
import logging

logger = logging.getLogger(__name__)

def resource_path(relative_path):
    logger.info("Resolving resource path for %s", relative_path)
    try:
        base_path = sys._MEIPASS
        logger.debug("Running in PyInstaller bundle, base_path=%s", base_path)
    except Exception:
        base_path = os.path.abspath(".")
        logger.debug("sys._MEIPASS unavailable, using cwd base_path=%s", base_path)

    return os.path.join(base_path, relative_path)