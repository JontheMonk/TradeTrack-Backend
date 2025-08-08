from typing import Generic, Optional, TypeVar
from pydantic import BaseModel
from core.errors import ErrorCode

T = TypeVar("T")

class ApiResponse(BaseModel, Generic[T]):
    success: bool
    data: Optional[T] = None
    code: Optional[str] = None
    message: Optional[str] = None

def ok(data: Optional[T] = None) -> ApiResponse[Optional[T]]:
    return ApiResponse[Optional[T]](success=True, data=data)

def fail(code: ErrorCode, message: str) -> ApiResponse[None]:
    return ApiResponse[None](success=False, code=code, message=message)