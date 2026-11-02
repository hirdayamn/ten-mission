"""Custom exceptions with HTTP status codes."""
from typing import Optional


class AppException(Exception):
    """Base application exception with HTTP status code."""
    status_code: int = 400
    detail: str = "Bad request"

    def __init__(self, detail: Optional[str] = None):
        self.detail = detail or self.detail
        super().__init__(self.detail)


# 404 Not Found
class NotFoundError(AppException):
    status_code = 404
    detail = "Resource not found"


# 409 Conflict
class ConflictError(AppException):
    status_code = 409
    detail = "Resource conflict"


# 422 Unprocessable Entity (for business rule violations)
class BusinessRuleError(AppException):
    status_code = 422
    detail = "Business rule violation"


# Specific error classes
class MemberNotFoundError(NotFoundError):
    detail = "Member not found"


class InventoryNotFoundError(NotFoundError):
    detail = "Inventory item not found"


class BookingNotFoundError(NotFoundError):
    detail = "Booking not found"


class MaxBookingsExceededError(BusinessRuleError):
    def __init__(self, current_count: int, limit: int):
        self.detail = f"Member has reached maximum bookings limit ({current_count}/{limit})"
        super().__init__(self.detail)


class InsufficientInventoryError(BusinessRuleError):
    detail = "Insufficient inventory available"


class InvalidBookingStateError(BusinessRuleError):
    detail = "Invalid booking state"


class ExpiredInventoryError(BusinessRuleError):
    detail = "Inventory item has expired"


class InactiveInventoryError(BusinessRuleError):
    detail = "Inventory item is not available"