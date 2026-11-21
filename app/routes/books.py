"""Book endpoints: list/search and single-book detail."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app import services
from app.database import get_db
from app.schemas import BookOut

router = APIRouter(prefix="/books", tags=["Books"])


@router.get("/", response_model=list[BookOut], summary="List or search books")
def list_books(
    search: str | None = Query(default=None, max_length=100, description="Part of a title (case-insensitive)"),
    db: Session = Depends(get_db),
):
    return services.list_books(db, search)


@router.get("/{book_id}", response_model=BookOut, summary="Get one book")
def get_book(book_id: str, db: Session = Depends(get_db)):
    return services.get_book(db, book_id)  # raises NotFoundError -> HTTP 404
