"""Seed script: creates the initial catalogue. Safe to run again and again.

Run from the project root:   python -m database.seed
"""
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import SessionLocal, init_db
from app.models import Book

# (id, title, total_copies) -> 3 books, 2 + 1 + 3 = 6 physical copies
CATALOGUE = [
    ("B1", "Python Basics", 2),
    ("B2", "Design Notes", 1),
    ("B3", "Data Stories", 3),
]


def seed_books(db: Session) -> int:
    """Insert any catalogue book that is missing. Returns how many were created."""
    created = 0
    for book_id, title, total in CATALOGUE:
        if db.get(Book, book_id) is None:  # already there? then skip: no duplicates
            db.add(Book(id=book_id, title=title, total_copies=total))
            created += 1
    db.commit()
    return created


def validate_catalogue(db: Session) -> list[str]:
    """Check the database matches the required catalogue. Returns a list of problems."""
    problems = []
    count = db.scalar(select(func.count(Book.id)))
    if count != 3:
        problems.append(f"Expected 3 books but found {count}.")
    total = db.scalar(select(func.coalesce(func.sum(Book.total_copies), 0)))
    if total != 6:
        problems.append(f"Expected 6 physical copies in total but found {total}.")
    for book_id, title, copies in CATALOGUE:
        book = db.get(Book, book_id)
        if book is None or book.title != title or book.total_copies != copies:
            problems.append(f"Book {book_id} does not match '{title}' with {copies} copies.")
    return problems


def main() -> None:
    init_db()
    with SessionLocal() as db:
        created = seed_books(db)
        problems = validate_catalogue(db)
        print(f"Books created this run: {created}")
        for book in db.scalars(select(Book).order_by(Book.id)):
            print(f"  {book.id}: {book.title} ({book.total_copies} copies)")
        if problems:
            print("VALIDATION FAILED:")
            for problem in problems:
                print(f"  - {problem}")
            raise SystemExit(1)
        print("Validation OK: 3 books, 6 physical copies.")


if __name__ == "__main__":
    main()
