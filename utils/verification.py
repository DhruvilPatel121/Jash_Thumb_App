from ctypes import c_bool, c_uint32, byref
import logging

class Verification:
    def __init__(self, scanner):
        self.scanner = scanner


    def initialize_matching(self):
        if not self.scanner.load_sdk():
            return False
        if not self.scanner.create():
            return False
        if not self.scanner.initialize():
            return False
        self.scanner.sdk.SGFPM_SetTemplateFormat(
            self.scanner.hfpm,
            0x0200
        )
        return True

    def terminate_matching(self):
        try:
            self.scanner.terminate()
        except:
            pass

    def match_template(self, captured_template, stored_template):
        try:

            score = c_uint32()
            result = self.scanner.sdk.SGFPM_GetMatchingScore(
                self.scanner.hfpm,
                captured_template,
                stored_template,
                byref(score)
            )
            if result == 0:
                return score.value
            return 0
        except Exception:
            return 0

    def identify_employee(self, captured_template, employees):
        try:
            for employee in employees:
                stored_template = employee.get("fingerprint_template")
                if not stored_template:
                    continue

                stored_template = bytes(stored_template)
                score = self.match_template(captured_template, stored_template)
                if score >= 100:
                    return employee
            return None
        except Exception as error:
            return None

    # These two methods are for the attendance system..

    def match_template_open_device(self, captured_template, stored_template):
        try:
            score = c_uint32()
            result = self.scanner.sdk.SGFPM_GetMatchingScore(
                self.scanner.hfpm, captured_template, stored_template, byref(score)
            )
            if result == 0:
                return score.value
            return 0
        except Exception as error:
            return 0

    def identify_patient_attendance(self, captured_template, patients):
        try:
            for patient in patients:
                stored_template = patient.get("fingerprint_template")
                if not stored_template:
                    continue

                stored_template = bytes(stored_template)
                score = self.match_template_open_device(captured_template, stored_template)
                if score >= 100:
                    return patient
            return None
        except Exception as error:
            logging.error(f"Identify Patient Attendance Error: {error}", exc_info=True)
            return None