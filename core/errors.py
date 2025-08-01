from enum import StrEnum
from fastapi import HTTPException
from core.errors import AppException

def map_app_exception(exc: AppException) -> HTTPException:
    return HTTPException(
        status_code=400,  # Always 400 for known app-level issues
        detail={
            "message": exc.message,
            "code": exc.code,
        }
    )

class ErrorCode(StrEnum):
    DB_ERROR = "DB_ERROR"
    EMPLOYEE_NOT_FOUND = "EMPLOYEE_NOT_FOUND"
    EMPLOYEE_ALREADY_EXISTS = "EMPLOYEE_ALREADY_EXISTS"
    UNKNOWN_ERROR = "UNKNOWN_ERROR"


# Custom exceptions

class AppException(Exception):
    def __init__(self, message: str, code: ErrorCode):
        self.message = message
        self.code = code
        super().__init__(message)


class DatabaseError(AppException):
    def __init__(self, message="Database error"):
        super().__init__(message, ErrorCode.DB_ERROR)


class EmployeeNotFound(AppException):
    def __init__(self, message="Employee not found"):
        super().__init__(message, ErrorCode.EMPLOYEE_NOT_FOUND)


class EmployeeAlreadyExists(AppException):
    def __init__(self, message="Employee already exists"):
        super().__init__(message, ErrorCode.EMPLOYEE_ALREADY_EXISTS)
