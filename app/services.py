"""Business logic shared by all routes (so no logic is duplicated).

Key rules implemented here:
  available copies = total_copies - (loans with returned = false)
  overdue          = current_day > due_day AND returned = false
  due_day          = checkout_day + 7
"""
from sqlalchemy import Boolean, Integer, String, func, insert, literal, select, update
from sqlalchemy.orm import Session

from app.models import Book, Loan
from app.schemas import BookOut, OverdueLoanOut

LOAN_PERIOD_DAYS = 7


class NotFoundError(Exception):
    """Something the client asked for does not exist (becomes HTTP 404)."""


class ConflictError(Exception):
    """The request is valid but clashes with the current state (becomes HTTP 409)."""


# ---------------------------------------------------------------- books ----
def _books_with_active_counts():
    """SELECT every book together with its number of ACTIVE loans (0 if none)."""
    active = (
        select(Loan.book_id.label("book_id"), func.count(Loan.id).label("active_loans"))
        .where(Loan.returned.is_(False))
        .group_by(Loan.book_id)
        .subquery()
    )
    return select(Book, func.coalesce(active.c.active_loans, 0)).outerjoin(
        active, active.c.book_id == Book.id
    )


def _to_book_out(book: Book, active_loans: int) -> BookOut:
    return BookOut(
        id=book.id,
        title=book.title,
        total_copies=book.total_copies,
        available_copies=book.total_copies - active_loans,  # derived, never stored
    )


def list_books(db: Session, search: str | None = None) -> list[BookOut]:
    """All books, optionally filtered by a case-insensitive title search."""
    stmt = _books_with_active_counts().order_by(Book.id)
    if search and search.strip():
        # Escape LIKE wildcards so searching for "%" or "_" matches literally.
        escaped = search.strip().replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        stmt = stmt.where(Book.title.ilike(f"%{escaped}%", escape="\\"))
    return [_to_book_out(book, active) for book, active in db.execute(stmt).all()]


def get_book(db: Session, book_id: str) -> BookOut:
    row = db.execute(_books_with_active_counts().where(Book.id == book_id)).first()
    if row is None:
        raise NotFoundError(f"Book '{book_id}' not found.")
    return _to_book_out(row[0], row[1])


# ---------------------------------------------------------------- loans ----
def borrow_book(db: Session, book_id: str, borrower_alias: str, checkout_day: int) -> Loan:
    """Create a loan if (and only if) a copy is available.

    The availability check and the INSERT are ONE SQL statement
    (INSERT ... SELECT ... WHERE available > 0). SQLite runs a single statement
    atomically, so two simultaneous requests can never both take the last copy
    and availability can never become negative.
    """
    book = db.get(Book, book_id)
    if book is None:
        raise NotFoundError(f"Book '{book_id}' not found.")

    due_day = checkout_day + LOAN_PERIOD_DAYS

    available = (
        select(Book.total_copies).where(Book.id == book_id).scalar_subquery()
        - select(func.count(Loan.id))
        .where(Loan.book_id == book_id, Loan.returned.is_(False))
        .scalar_subquery()
    )
    stmt = (
        insert(Loan)
        .from_select(
            ["book_id", "borrower_alias", "checkout_day", "due_day", "returned"],
            select(
                literal(book_id, String),
                literal(borrower_alias, String),
                literal(checkout_day, Integer),
                literal(due_day, Integer),
                literal(False, Boolean),
            ).where(available > 0),
        )
        .returning(Loan.id)
    )

    try:
        new_loan_id = db.execute(stmt).scalar_one_or_none()
        if new_loan_id is None:  # the WHERE clause found no free copy: nothing inserted
            db.rollback()
            raise ConflictError(f"No copies of '{book.title}' are currently available.")
        db.commit()
    except ConflictError:
        raise
    except Exception:
        db.rollback()
        raise

    return db.get(Loan, new_loan_id)


def return_loan(db: Session, loan_id: int) -> Loan:
    """Mark a loan as returned. Returning twice is rejected with a conflict."""
    loan = db.get(Loan, loan_id)
    if loan is None:
        raise NotFoundError(f"Loan {loan_id} not found.")

    try:
        # "AND returned = false" makes the update itself refuse a duplicate return,
        # even if two requests arrive at the same moment.
        result = db.execute(
            update(Loan).where(Loan.id == loan_id, Loan.returned.is_(False)).values(returned=True)
        )
        if result.rowcount == 0:
            db.rollback()
            raise ConflictError(f"Loan {loan_id} has already been returned.")
        db.commit()
    except ConflictError:
        raise
    except Exception:
        db.rollback()
        raise

    db.refresh(loan)
    return loan


# -------------------------------------------------------------- overdue ----
def overdue_loans(db: Session, current_day: int) -> list[OverdueLoanOut]:
    """Loans that are overdue on `current_day`: not returned AND current_day > due_day."""
    stmt = (
        select(Loan, Book.title)
        .join(Book, Book.id == Loan.book_id)
        .where(Loan.returned.is_(False), Loan.due_day < current_day)
        .order_by(Loan.due_day, Loan.id)
    )
    return [
        OverdueLoanOut(
            loan_id=loan.id,
            book_id=loan.book_id,
            book_title=title,
            borrower_alias=loan.borrower_alias,
            checkout_day=loan.checkout_day,
            due_day=loan.due_day,
            current_day=current_day,
            overdue=current_day > loan.due_day,  # derived on the fly
        )
        for loan, title in db.execute(stmt).all()
    ]
