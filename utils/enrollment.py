import ctypes
from ctypes import Structure, c_ushort, c_uint32, byref
import logging

class SGFingerInfo(Structure):
    _fields_ = [
        ("FingerNumber", c_ushort),
        ("ViewNumber", c_ushort),
        ("ImpressionType", c_ushort),
        ("ImageQuality", c_ushort),
    ]


class Enrollment:
    def __init__(self, scanner):
        self.scanner = scanner

    def get_max_template_size(self):
        try:
            template_size = c_uint32()
            result = self.scanner.sdk.SGFPM_GetMaxTemplateSize(
                self.scanner.hfpm, byref(template_size)
            )
            return template_size.value if result == 0 else None
        except Exception as error:
            logging.error(f"Get Max Template Size Error: {error}", exc_info=True)
            return None

    def create_template(self, image_buffer):
        try:
            template_size = self.get_max_template_size()
            if not template_size:
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
            return template_buffer if result == 0 else None
        except Exception as error:
            logging.error(f"Create Template Error: {error}", exc_info=True)
            return None

    def create_template_bytes(self, image_buffer):
        template = self.create_template(image_buffer)
        return bytes(template) if template else None