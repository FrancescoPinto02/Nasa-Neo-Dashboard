from datetime import date

import pytest

from app.core.errors import InvalidDateRangeError
from app.utils.dates import iter_date_chunks, validate_date_range


def test_iter_date_chunks_splits_inclusive_range() -> None:
    chunks = list(
        iter_date_chunks(
            start_date=date(2026, 5, 1),
            end_date=date(2026, 5, 10),
            max_days=7,
        )
    )

    assert chunks == [
        (date(2026, 5, 1), date(2026, 5, 7)),
        (date(2026, 5, 8), date(2026, 5, 10)),
    ]


def test_iter_date_chunks_keeps_short_range_as_single_chunk() -> None:
    chunks = list(
        iter_date_chunks(
            start_date=date(2026, 5, 1),
            end_date=date(2026, 5, 3),
            max_days=7,
        )
    )

    assert chunks == [
        (date(2026, 5, 1), date(2026, 5, 3)),
    ]


def test_validate_date_range_rejects_inverted_dates() -> None:
    with pytest.raises(InvalidDateRangeError):
        validate_date_range(
            start_date=date(2026, 5, 10),
            end_date=date(2026, 5, 1),
            max_range_days=90,
        )


def test_validate_date_range_rejects_too_large_range() -> None:
    with pytest.raises(InvalidDateRangeError):
        validate_date_range(
            start_date=date(2026, 1, 1),
            end_date=date(2026, 4, 30),
            max_range_days=90,
        )