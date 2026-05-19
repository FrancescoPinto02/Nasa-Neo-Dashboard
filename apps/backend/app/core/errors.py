class AppError(Exception):
    """Base class for application-level exceptions."""


class InvalidDateRangeError(AppError, ValueError):
    """Raised when the requested date range is invalid."""


class ExternalServiceError(AppError):
    """Raised when an external service cannot be reached or returns invalid data."""