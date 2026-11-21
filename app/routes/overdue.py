"""Overdue report endpoint."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app import services
from app.database import get_db
from app.schemas import OverdueLoanOut

router = APIRouter(prefix="/overdue", tags=["Overdue"])


@router.get("/", response_model=list[OverdueLoanOut], summary="Overdue loans on a given day")
def overdue_report(
    current_day: int = Query(..., ge=0, le=1_000_000, description="The day to evaluate, e.g. 11"),
    db: Session = Depends(get_db),
):
    return services.overdue_loans(db, current_day)
