from typing import Generic, Optional, TypeVar
from pydantic import BaseModel
from core.errors import ErrorCode

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """
    Standardized wrapper for all API responses.

    This model ensures that every endpoint returns a predictable JSON structure,
    regardless of success or failure. Successful responses carry a typed
    payload under `data`, while failed responses include an application-level
    error code and human-readable message.

    Attributes
    ----------
    success : bool
        Indicates whether the request completed successfully.
    data : Optional[T]
        Payload returned on success. For empty responses, this is `None`.
    code : Optional[str]
        Error code used when `success=False`. Aligns with `ErrorCode`.
    message : Optional[str]
        Human-readable description of the success or error condition.
    """
    success: bool
    data: Optional[T] = None
    code: Optional[str] = None
    message: Optional[str] = None


def ok(data: Optional[T] = None) -> ApiResponse[Optional[T]]:
    """
    Create a successful API response.

    Parameters
    ----------
    data : Optional[T]
        Optional payload to include in the response. Defaults to `None`.

    Returns
    -------
    ApiResponse[Optional[T]]
        A standardized success response containing the given payload.
    """
    return ApiResponse[Optional[T]](success=True, data=data)


def fail(code: ErrorCode, message: str) -> ApiResponse[None]:
    """
    Create a standardized error API response.

    Parameters
    ----------
    code : ErrorCode
        Application-level error identifier describing the type of failure.
    message : str
        Human-readable explanation of the failure.

    Returns
    -------
    ApiResponse[None]
        A failure response with no payload, containing the provided error
        code and message.

    Notes
    -----
    This function is typically used by global exception handlers to convert
    domain errors into consistent API responses.
    """
    return ApiResponse[None](success=False, code=code, message=message)
