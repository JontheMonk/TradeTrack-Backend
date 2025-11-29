from enum import StrEnum
from fastapi import status

class ErrorCode(StrEnum):
    """
    Enumeration of all application-level error codes returned by the API.

    These codes are used in error responses and logs to give clients and
    developers a consistent way to identify failure types regardless of what
    HTTP status code was returned.
    """
    DB_ERROR = "DB_ERROR"
    EMPLOYEE_NOT_FOUND = "EMPLOYEE_NOT_FOUND"
    EMPLOYEE_ALREADY_EXISTS = "EMPLOYEE_ALREADY_EXISTS"
    FACE_CONFIDENCE_TOO_LOW = "FACE_CONFIDENCE_TOO_LOW"
    UNAUTHORIZED = "UNAUTHORIZED"
    UNKNOWN_ERROR = "UNKNOWN_ERROR"


class AppException(Exception):
    """
    Base class for all structured application errors.

    Attributes:
        message: Human-readable error description.
        code: An ErrorCode enum describing the type of failure.
        http_status: HTTP status code returned by this exception.
                     Subclasses should override this value.

    Any subclass represents a *controlled* failure state that the application
    explicitly understands and expects to return to API clients.
    """
    http_status = status.HTTP_500_INTERNAL_SERVER_ERROR  # default override-able

    def __init__(self, message: str, code: ErrorCode):
        self.message = message
        self.code = code
        super().__init__(message)


# --- Specific exceptions ---

class DatabaseError(AppException):
    """
    Raised when a database operation fails (connection errors, failed queries, etc.).

    This is treated as an internal server error and returned as a 500 to clients
    with the error code DB_ERROR.
    """
    http_status = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(self, message="Database error"):
        super().__init__(message, ErrorCode.DB_ERROR)


class EmployeeNotFound(AppException):
    """
    Raised when the requested employee ID or prefix lookup cannot be found.

    Returns an HTTP 404 and the EMPLOYEE_NOT_FOUND error code.
    """
    http_status = status.HTTP_404_NOT_FOUND

    def __init__(self, message="Employee not found"):
        super().__init__(message, ErrorCode.EMPLOYEE_NOT_FOUND)


class EmployeeAlreadyExists(AppException):
    """
    Raised when attempting to insert an employee that already exists
    (typically triggered by a unique constraint or name/ID validation).

    Returns an HTTP 409 Conflict.
    """
    http_status = status.HTTP_409_CONFLICT

    def __init__(self, message="Employee already exists"):
        super().__init__(message, ErrorCode.EMPLOYEE_ALREADY_EXISTS)


class FaceConfidenceTooLow(AppException):
    """
    Raised when the face embedding comparison returns a similarity score below
    the acceptance threshold defined by the system.

    Returned as HTTP 400 Bad Request because the input is valid but does not
    meet the required biometric confidence level.
    """
    http_status = status.HTTP_400_BAD_REQUEST

    def __init__(self, message="Face match confidence too low"):
        super().__init__(message, ErrorCode.FACE_CONFIDENCE_TOO_LOW)

class Unauthorized(AppException):
    """
    Raised when a client provides no admin key or an invalid admin key.

    Corresponds to HTTP 401 Unauthorized.
    """
    http_status = status.HTTP_401_UNAUTHORIZED

    def __init__(self, message="Unauthorized"):
        super().__init__(message, ErrorCode.UNAUTHORIZED)

class ServerMisconfigured(AppException):
    """
    Raised when the server itself is misconfigured (e.g., missing secrets,
    missing env vars). This is a server error, not the client's fault.

    Corresponds to HTTP 500.
    """
    http_status = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(self, message="Server misconfigured"):
        super().__init__(message, ErrorCode.UNKNOWN_ERROR)


