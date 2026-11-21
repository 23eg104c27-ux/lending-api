"""Loan endpoints: borrow a book and return a book."""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app import services
from app.database import get_db
from app.schemas import LoanCreate, LoanOut

router = APIRouter(prefix="/loans", tags=["Loans"])


@router.post("/", response_model=LoanOut, status_code=status.HTTP_201_CREATED, summary="Borrow a book")
def borrow(payload: LoanCreate, db: Session = Depends(get_db)):
    loan = services.borrow_book(db, payload.book_id, payload.borrower_alias, payload.checkout_day)
    return LoanOut.model_validate(loan)


@router.post("/{loan_id}/return", response_model=LoanOut, summary="Return a borrowed book")
def return_book(loan_id: int, db: Session = Depends(get_db)):
    loan = services.return_loan(db, loan_id)
    return LoanOut.model_validate(loan)
