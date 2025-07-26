from typing import Optional, TypeVar, Generic

T = TypeVar("T")

class VoidResult:
    def __init__(self, success: bool, message: Optional[str] = None, code: Optional[str] = None):
        self.success = success
        self.message = message
        self.code = code

    @classmethod
    def ok(cls, message: str = "") -> "VoidResult":
        return cls(True, message)

    @classmethod
    def fail(cls, message: str, code: str = "UNKNOWN_ERROR") -> "VoidResult":
        return cls(False, message, code)


class OperationResult(Generic[T]):
    def __init__(self, success: bool, message: Optional[str] = None, code: Optional[str] = None, data: Optional[T] = None):
        self.success = success
        self.message = message
        self.code = code
        self.data = data

    @classmethod
    def ok(cls, message: str = "", data: Optional[T] = None) -> "OperationResult[T]":
        return cls(True, message, data=data)

    @classmethod
    def fail(cls, message: str, code: str = "UNKNOWN_ERROR") -> "OperationResult[T]":
        return cls(False, message, code=code)
