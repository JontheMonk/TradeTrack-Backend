from enum import StrEnum
from fastapi import status
import logging

logger = logging.getLogger(__name__)

class ErrorCode(StrEnum):
    DB_ERROR = "DB_ERROR"
    EMPLOYEE_NOT_FOUND = "EMPLOYEE_NOT_FOUND"
    EMPLOYEE_ALREADY_EXISTS = "EMPLOYEE_ALREADY_EXISTS"
    FACE_CONFIDENCE_TOO_LOW = "FACE_CONFIDENCE_TOO_LOW"
    UNKNOWN_ERROR = "UNKNOWN_ERROR"

class AppException(Exception):
    http_status = status.HTTP_500_INTERNAL_SERVER_ERROR  # default for base
    def __init__(self, message: str, code: ErrorCode):
        self.message = message
        self.code = code
        super().__init__(message)

# --- Specific exceptions ---
class DatabaseError(AppException):
    http_status = status.HTTP_500_INTERNAL_SERVER_ERROR
    def __init__(self, message="Database error"):
        super().__init__(message, ErrorCode.DB_ERROR)

class EmployeeNotFound(AppException):
    http_status = status.HTTP_404_NOT_FOUND
    def __init__(self, message="Employee not found"):
        super().__init__(message, ErrorCode.EMPLOYEE_NOT_FOUND)

class EmployeeAlreadyExists(AppException):
    http_status = status.HTTP_409_CONFLICT
    def __init__(self, message="Employee already exists"):
        super().__init__(message, ErrorCode.EMPLOYEE_ALREADY_EXISTS)

class FaceConfidenceTooLow(AppException):
    http_status = status.HTTP_400_BAD_REQUEST
    def __init__(self, message="Face match confidence too low"):
        super().__init__(message, ErrorCode.FACE_CONFIDENCE_TOO_LOW)
