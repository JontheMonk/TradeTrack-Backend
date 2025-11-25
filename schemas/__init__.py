from .input.employee_input import EmployeeInput
from .input.verify_face_request import VerifyFaceRequest
from .output.employee_result import EmployeeResult

__all__ = ["EmployeeInput", "VerifyFaceRequest", "EmployeeResult"]
"""
Public schema exports for the `schemas` package.

This module re-exports the most commonly used request and response models so
consumers can simply import from `schemas` instead of referencing deeper
submodules such as `schemas.input.*` or `schemas.output.*`.

Exposed models:
    EmployeeInput:
        Payload for creating or updating an employee.

    VerifyFaceRequest:
        Payload for verifying a live face embedding against a stored one.

    EmployeeResult:
        Simplified employee representation returned by search endpoints.
"""
