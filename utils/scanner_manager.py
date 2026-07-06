import os
import ctypes
from ctypes import c_void_p, byref
from utils.resource_path import resource_path
import logging

logger = logging.getLogger(__name__)

class ScannerManager:

    def __init__(self):
        logger.info("Initializing ScannerManager")
        self.sdk = None
        self.hfpm = None
        self.sdk_loaded = False
        self.device_connected = False
        self.current_mode = "IDLE"
        self.image_size = 300 * 400
        self.image_buffer = (ctypes.c_ubyte * self.image_size)()

    def load_sdk(self):
        if self.sdk_loaded:
            logger.debug("SDK already loaded")
            return True
        try:
            sdk_path = resource_path("sdk")
            logger.info("Loading scanner SDK from path: %s", sdk_path)
            os.add_dll_directory(sdk_path)
            self.sdk = ctypes.WinDLL(os.path.join(sdk_path, "sgfplib.dll"))
            self.algorithm = ctypes.WinDLL(os.path.join(sdk_path, "sgfpamx.dll"))
            logger.info("SDK Loaded Successfully")
            self.sdk_loaded = True
            return True
        except Exception as error:
            logger.error("SDK Load Failed", exc_info=True)
            return False

    def create(self):
        logger.info("Creating scanner handle")
        try:
            self.hfpm = c_void_p()
            result = self.sdk.SGFPM_Create(byref(self.hfpm))
            if result == 0:
                logger.debug("Scanner handle created successfully")
                return True
            logger.warning("Scanner handle creation failed with result=%s", result)
            return False
        except Exception as error:
            logger.error("Scanner create exception", exc_info=True)
            return False

    def initialize(self):
        logger.info("Initializing scanner")
        try:
            result = self.sdk.SGFPM_Init(self.hfpm, 0x06)
            if result == 0:
                logger.debug("Scanner initialized successfully")
                return True
            logger.warning("Scanner initialization failed with result=%s", result)
            return False
        except Exception as error:
            logger.error("Scanner initialize exception", exc_info=True)
            return False

    def open_device(self):
        logger.info("Opening scanner device")
        try:
            result = self.sdk.SGFPM_OpenDevice(self.hfpm, 0)
            if result == 0:
                self.device_connected = True
                logger.info("Scanner device opened successfully")
                return True
            logger.error("Scanner Open Failed. Result=%s", result)
            return False
        except Exception as error:
            logger.error("Open Device Exception", exc_info=True)
            return False

    def get_image_quality(self, image_buffer):
        logger.debug("Getting image quality")
        try:
            quality = ctypes.c_uint32(0)
            result = self.sdk.SGFPM_GetImageQuality(self.hfpm, 300, 400, image_buffer, byref(quality))
            if result == 0:
                logger.debug("Image quality score=%s", quality.value)
                return quality.value
            logger.warning("GetImageQuality failed with result=%s", result)
            return 0
        except Exception as error:
            logger.error("Get image quality exception", exc_info=True)
            return 0

    def capture_image(self):
        logger.info("Capturing scanner image")
        try:
            image_size = 300 * 400
            image_buffer = (ctypes.c_ubyte * image_size)()
            result = self.sdk.SGFPM_GetImage(self.hfpm, image_buffer)
            if result == 0:
                quality_score = self.get_image_quality(image_buffer)
                if quality_score < 65:
                    logger.warning("Captured image quality too low: %s", quality_score)
                    return None, "Try again, image is not clear."
                logger.debug("Captured image successfully with quality=%s", quality_score)
                return image_buffer, "Success"
            logger.warning("Capture image request returned result=%s", result)
            return None, "Please place your finger on the scanner."
        except Exception as error:
            logger.error("Capture image exception", exc_info=True)
            return None, f"Error: {str(error)}"

    def capture_image_attend(self):
        logger.info("Capturing attendance scanner image")
        try:
            result = self.sdk.SGFPM_GetImage(self.hfpm, self.image_buffer)
            if result == 0:
                quality_score = self.get_image_quality(self.image_buffer)
                if quality_score < 20:
                    logger.warning("Attendance capture image quality too low: %s", quality_score)
                    return None, "Try again, image is not clear."
                logger.debug("Attendance capture succeeded with quality=%s", quality_score)
                return self.image_buffer, "Success"
            logger.warning("Attendance capture result=%s", result)
            return None, "Please place your finger on the scanner."
        except Exception as error:
            logger.error("Capture attendance image exception", exc_info=True)
            return None, f"Error: {str(error)}"

    def close_device(self):
        logger.info("Closing scanner device")
        try:
            result = self.sdk.SGFPM_CloseDevice(self.hfpm)
            if result == 0:
                self.device_connected = False
                logger.debug("Scanner device closed successfully")
                return True
            logger.warning("Close device failed with result=%s", result)
            return False
        except Exception as error:
            logger.error("Close device exception", exc_info=True)
            return False

    def terminate(self):
        logger.info("Terminating scanner session")
        try:
            result = self.sdk.SGFPM_Terminate(self.hfpm)
            if result == 0:
                self.hfpm = None
                logger.debug("Scanner terminated successfully")
                return True
            logger.warning("Terminate failed with result=%s", result)
            return False
        except Exception as error:
            logger.error("Terminate exception", exc_info=True)
            return False

    def is_connected(self):
        logger.debug("Checking scanner connection status: %s", self.device_connected)
        return self.device_connected

