from ctypes import c_uint32, byref
import logging

logger = logging.getLogger(__name__)

class Verification:
    def __init__(self, scanner):
        logger.info("Initializing Verification")
        self.scanner = scanner

    def initialize_matching(self):
        logger.info("Initializing matching in Verification")
        if not self.scanner.load_sdk():
            logger.warning("Scanner SDK failed to load during verification initialization")
            return False
        if not self.scanner.create():
            logger.warning("Scanner create failed during verification initialization")
            return False
        if not self.scanner.initialize():
            logger.warning("Scanner initialize failed during verification initialization")
            return False
        self.scanner.sdk.SGFPM_SetTemplateFormat(
            self.scanner.hfpm,
            0x0200
        )
        logger.debug("Verification template format set")
        return True

    def terminate_matching(self):
        logger.info("Terminating verification matching")
        try:
            self.scanner.terminate()
        except Exception as error:
            logger.error("Error terminating verification matching", exc_info=True)

    def match_template(self, captured_template, stored_template):
        logger.info("Matching fingerprint templates")
        try:
            score = c_uint32()
            result = self.scanner.sdk.SGFPM_GetMatchingScore(
                self.scanner.hfpm,
                captured_template,
                stored_template,
                byref(score)
            )
            if result == 0:
                logger.debug("Template match score=%s", score.value)
                return score.value
            logger.warning("Match template failed with result=%s", result)
            return 0
        except Exception as error:
            logger.error("Match template exception", exc_info=True)
            return 0

    def identify_employee(self, captured_template, employees):
        logger.info("Identifying employee with captured template")
        try:
            for employee in employees:
                stored_template = employee.get("fingerprint_template")
                if not stored_template:
                    logger.debug("Skipping employee without stored template")
                    continue

                stored_template = bytes(stored_template)
                score = self.match_template(captured_template, stored_template)
                if score >= 100:
                    logger.info("Employee identified with score=%s", score)
                    return employee
            logger.debug("No matching employee found")
            return None
        except Exception as error:
            logger.error("Identify Employee Error", exc_info=True)
            return None

    def match_template_open_device(self, captured_template, stored_template):
        logger.info("Matching fingerprint templates with open device")
        try:
            score = c_uint32()
            result = self.scanner.sdk.SGFPM_GetMatchingScore(
                self.scanner.hfpm, captured_template, stored_template, byref(score)
            )
            if result == 0:
                logger.debug("Open device match score=%s", score.value)
                return score.value
            logger.warning("Match template open device failed with result=%s", result)
            return 0
        except Exception as error:
            logger.error("Match template open device exception", exc_info=True)
            return 0

    def identify_patient_attendance(self, captured_template, patients):
        logger.info("Identifying patient for attendance with captured template")
        try:
            for patient in patients:
                stored_template = patient.get("fingerprint_template")
                if not stored_template:
                    logger.debug("Skipping patient without stored template")
                    continue

                stored_template = bytes(stored_template)
                score = self.match_template_open_device(captured_template, stored_template)
                if score >= 100:
                    logger.info("Patient identified for attendance with score=%s", score)
                    return patient
            logger.debug("No matching patient found for attendance")
            return None
        except Exception as error:
            logger.error("Identify Patient Attendance Error", exc_info=True)
            return None