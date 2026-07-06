import ctypes
from ctypes import Structure, c_ushort, c_uint32, byref
import logging

logger = logging.getLogger(__name__)

class SGFingerInfo(Structure):
    _fields_ = [
        ("FingerNumber", c_ushort),
        ("ViewNumber", c_ushort),
        ("ImpressionType", c_ushort),
        ("ImageQuality", c_ushort),
    ]


class Enrollment:
    def __init__(self, scanner):
        logger.info("Initializing Enrollment")
        self.scanner = scanner

    def get_max_template_size(self):
        logger.info("Getting max template size")
        try:
            template_size = c_uint32()
            result = self.scanner.sdk.SGFPM_GetMaxTemplateSize(
                self.scanner.hfpm, byref(template_size)
            )
            if result != 0:
                logger.warning("Failed to retrieve max template size, SDK result=%s", result)
            else:
                logger.debug("Max template size retrieved: %s", template_size.value)
            return template_size.value if result == 0 else None
        except Exception as error:
            logger.error("Get Max Template Size Error", exc_info=True)
            return None

    def create_template(self, image_buffer):
        logger.info("Creating fingerprint template")
        try:
            template_size = self.get_max_template_size()
            if not template_size:
                logger.warning("Template creation aborted due to invalid template size")
                return None
            finger_info = SGFingerInfo(
                FingerNumber=1, ViewNumber=1, ImpressionType=0, ImageQuality=0
            )
            template_buffer = (ctypes.c_ubyte * template_size)()
            result = self.scanner.sdk.SGFPM_CreateTemplate(
                self.scanner.hfpm,
                byref(finger_info),
                image_buffer,
                template_buffer,
            )
            if result != 0:
                logger.warning("SGFPM_CreateTemplate failed with result=%s", result)
            else:
                logger.debug("Fingerprint template created successfully")
            return template_buffer if result == 0 else None
        except Exception as error:
            logger.error("Create Template Error", exc_info=True)
            return None

    def create_template_bytes(self, image_buffer):
        template = self.create_template(image_buffer)
        return bytes(template) if template else None