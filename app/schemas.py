"""Pydantic schemas = the shape of data coming IN and going OUT of the API.

Pydantic checks incoming data BEFORE any database work happens, so invalid
requests are rejected with HTTP 422 and never touch the database.
"""
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

# A fictional alias: 1-30 letters, digits, "_" or "-". Because "@" and "." are not
# allowed, e-mail addresses and phone-number-like text are rejected automatically.
BorrowerAlias = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=30, pattern=r"^[A-Za-z0-9_-]+$"),
]
BookId = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=10)]
# strict=True: the JSON must contain a real integer (not "3", not true, not 3.5).
Day = Annotated[int, Field(strict=True, ge=0, le=1_000_000)]


class LoanCreate(BaseModel):
    """Body of POST /loans/."""

    model_config = ConfigDict(
        extra="forbid",  # unknown fields (e.g. "email") are rejected: no personal data
        json_schema_extra={
            "example": {"book_id": "B1", "borrower_alias": "finch", "checkout_day": 3}
        },
    )

    book_id: BookId
    borrower_alias: BorrowerAlias
    checkout_day: Day


class BookOut(BaseModel):
    id: str
    title: str
    total_copies: int
    available_copies: int  # DERIVED: total_copies - active loans


class LoanOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    book_id: str
    borrower_alias: str
    checkout_day: int
    due_day: int
    returned: bool


class OverdueLoanOut(BaseModel):
    loan_id: int
    book_id: str
    book_title: str
    borrower_alias: str
    checkout_day: int
    due_day: int
    current_day: int
    overdue: bool  # DERIVED: current_day > due_day (and not returned)
