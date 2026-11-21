"""Application entry point. Start with:  python -m uvicorn app.main:app --reload"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.database import init_db
from app.routes import books, loans, overdue
from app.services import ConflictError, NotFoundError

logger = logging.getLogger("lending_api")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()  # make sure the tables exist when the server starts
    yield


app = FastAPI(
    title="Library Lending API",
    version="1.0.0",
    description=(
        "Lending API for a small fictional library. Availability and overdue status "
        "are calculated from loan records and are never stored."
    ),
    lifespan=lifespan,
)

app.include_router(books.router)
app.include_router(loans.router)
app.include_router(overdue.router)


@app.exception_handler(NotFoundError)
async def handle_not_found(_request: Request, exc: NotFoundError):
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(ConflictError)
async def handle_conflict(_request: Request, exc: ConflictError):
    return JSONResponse(status_code=409, content={"detail": str(exc)})


@app.exception_handler(SQLAlchemyError)
async def handle_database_error(_request: Request, exc: SQLAlchemyError):
    logger.exception("Database error: %s", exc)  # details go to the log, not to the client
    return JSONResponse(status_code=500, content={"detail": "A database error occurred. Please try again."})


@app.get("/", tags=["Info"], summary="API status")
def root():
    return {"message": "Library Lending API is running. Open /docs for the interactive documentation."}
