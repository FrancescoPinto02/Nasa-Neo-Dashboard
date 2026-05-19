from collections.abc import Iterator
from datetime import date, timedelta

from app.core.errors import InvalidDateRangeError


def validate_date_range(start_date: date, end_date: date, max_range_days: int) -> None:
    """Validate an inclusive date range.

    Args:
        start_date: First day included in the query.
        end_date: Last day included in the query.
        max_range_days: Maximum number of days allowed by our application.

    Raises:
        InvalidDateRangeError: If dates are inverted or the range is too large.
    """
    if start_date > end_date:
        raise InvalidDateRangeError("start_date must be less than or equal to end_date.")

    total_days = (end_date - start_date).days + 1

    if total_days > max_range_days:
        raise InvalidDateRangeError(
            f"The requested range contains {total_days} days, "
            f"but the maximum allowed range is {max_range_days} days."
        )


def iter_date_chunks(
    start_date: date,
    end_date: date,
    max_days: int,
) -> Iterator[tuple[date, date]]:
    """Split an inclusive date range into smaller inclusive chunks.

    NASA NeoWs accepts a limited date range per request. This helper keeps
    that constraint outside the API route and service orchestration code.

    Example:
        2026-05-01 to 2026-05-10 with max_days=7 becomes:
        - 2026-05-01 to 2026-05-07
        - 2026-05-08 to 2026-05-10
    """
    if max_days < 1:
        raise ValueError("max_days must be greater than or equal to 1.")

    current_start = start_date

    while current_start <= end_date:
        current_end = min(current_start + timedelta(days=max_days - 1), end_date)
        yield current_start, current_end
        current_start = current_end + timedelta(days=1)