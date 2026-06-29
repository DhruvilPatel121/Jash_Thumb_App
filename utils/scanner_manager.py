import os
import ctypes
from ctypes import c_void_p, byref
from utils.resource_path import resource_path
import logging
class ScannerManager:

    def __init__(self):
        self.sdk = None
        self.hfpm = None
        self.sdk_loaded = False
        self.device_connected = False
        self.current_mode = "IDLE"
        self.image_size = 300 * 400
        self.image_buffer = (ctypes.c_ubyte * self.image_size)()


    def load_sdk(self):
        if self.sdk_loaded:
            return True
        try:
            sdk_path = resource_path("sdk")
            logging.info(f"SDK PATH: {sdk_path}")
            os.add_dll_directory(sdk_path)
            self.sdk = ctypes.WinDLL(os.path.join(sdk_path, "sgfplib.dll"))
            self.algorithm = ctypes.WinDLL(os.path.join(sdk_path, "sgfpamx.dll"))
            logging.info("SDK Loaded Successfully")
            self.sdk_loaded = True
            return True
        except Exception as error:
            logging.error(f"SDK Load Failed: {error}",exc_info=True)
            return False

    def create(self):
        try:
            self.hfpm = c_void_p()
            result = self.sdk.SGFPM_Create(byref(self.hfpm))
            if result == 0:
                return True
            return False
        except Exception as error:
            return False

    def initialize(self):
        try:
            result = self.sdk.SGFPM_Init(self.hfpm, 0x06)
            if result == 0:
                return True
            return False
        except Exception as error:
            return False

    def open_device(self):
        try:
            result = self.sdk.SGFPM_OpenDevice(self.hfpm, 0)
            if result == 0:
                self.device_connected = True
                return True
            logging.error(f"Scanner Open Failed. Result={result}")
            return False
        except Exception as error:
            logging.error(f"Open Device Exception: {error}",exc_info=True)
            return False

    
    def get_image_quality(self, image_buffer):
        try:
            quality = ctypes.c_uint32(0)
            result = self.sdk.SGFPM_GetImageQuality(self.hfpm, 300, 400, image_buffer, byref(quality))
            if result == 0:
                return quality.value
            return 0
        except Exception as error:
            return 0

    def capture_image(self):
        try:
            image_size = 300 * 400
            image_buffer = (ctypes.c_ubyte * image_size)()
            result = self.sdk.SGFPM_GetImage(self.hfpm, image_buffer)
            if result == 0:
                quality_score = self.get_image_quality(image_buffer)
                
                if quality_score < 70:
                    return None, "Try again, image is not clear."                
                return image_buffer, "Success"
            
            return None, "Please place your finger on the scanner."
        except Exception as error:
            return None, f"Error: {str(error)}"

    def capture_image_attend(self):
        try:
            result = self.sdk.SGFPM_GetImage(self.hfpm, self.image_buffer)
            
            if result == 0:
                quality_score = self.get_image_quality(self.image_buffer)
                
                if quality_score < 20:
                    return None, "Try again, image is not clear."
                return self.image_buffer, "Success"
            
            return None, "Please place your finger on the scanner."
        except Exception as error:
            return None, f"Error: {str(error)}"
    
        
    def close_device(self):
        try:
            result = self.sdk.SGFPM_CloseDevice(self.hfpm)
            if result == 0:
                self.device_connected = False
                return True
            return False
        except Exception as error:
            return False

    def terminate(self):
        try:
            result = self.sdk.SGFPM_Terminate(self.hfpm)
            if result == 0:
                self.hfpm = None
                return True
            return False
        except Exception as error:
            return False

    def is_connected(self):
        return self.device_connected

