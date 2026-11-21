"""SQLAlchemy models = the two database tables.

Only FACTS are stored here. There is deliberately NO 'available' column on
Book and NO 'is_overdue' column on Loan: both are calculated from the loans
every time they are needed (see app/services.py).
"""
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    ForeignKey,
    Index,
    Integer,
    String,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Book(Base):
    __tablename__ = "books"

    id: Mapped[str] = mapped_column(String(10), primary_key=True)  # e.g. "B1"
    title: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)
    total_copies: Mapped[int] = mapped_column(Integer, nullable=False)

    loans: Mapped[list["Loan"]] = relationship(back_populates="book")

    __table_args__ = (
        CheckConstraint("total_copies >= 0", name="ck_books_total_copies_non_negative"),
    )


class Loan(Base):
    __tablename__ = "loans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    book_id: Mapped[str] = mapped_column(ForeignKey("books.id"), nullable=False)
    borrower_alias: Mapped[str] = mapped_column(String(30), nullable=False)
    checkout_day: Mapped[int] = mapped_column(Integer, nullable=False)
    due_day: Mapped[int] = mapped_column(Integer, nullable=False)
    returned: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=text("0")
    )

    book: Mapped["Book"] = relationship(back_populates="loans")

    __table_args__ = (
        CheckConstraint("length(borrower_alias) > 0", name="ck_loans_alias_not_empty"),
        CheckConstraint("checkout_day >= 0", name="ck_loans_checkout_day_non_negative"),
        CheckConstraint("due_day > checkout_day", name="ck_loans_due_after_checkout"),
        # Speeds up "how many active loans does this book have?"
        Index("ix_loans_book_id_returned", "book_id", "returned"),
        # Speeds up the overdue report.
        Index("ix_loans_returned_due_day", "returned", "due_day"),
    )
