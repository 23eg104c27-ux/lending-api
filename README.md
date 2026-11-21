# Library Lending API

A REST API for a small fictional library, built with Python, FastAPI and SQLite. It lets users view and search books, borrow and return them, and list overdue loans. This project was prepared for the CareerSwami Python & Backend Engineering internship (Project 1: *Build a Lending API That Knows What Is Overdue*).

## Problem statement
A library needs to know, at any moment, how many copies of each book are free and which loans are late. If "available" and "overdue" were stored as extra columns, they could drift out of sync with the real loans. This API avoids that by storing only facts (books and loans) and **calculating** availability and overdue status every time they are requested.

## Objectives
- Store books and loans in a proper relational database.
- Calculate availability and overdue status dynamically.
- Validate all input before it reaches the database.
- Prevent over-borrowing, even with simultaneous requests.
- Provide automatic interactive documentation and a full automated test suite.

## Features
- List books with available copies; case-insensitive title search; single-book detail.
- Borrow a book (`due_day = checkout_day + 7`) and return a book.
- Overdue report for any evaluation day via `?current_day=`.
- Fictional borrower aliases only; no personal data is requested or stored.
- Readable errors with correct HTTP status codes (404, 409, 422).

## Technologies
Python 3.11, FastAPI 0.115.6, Uvicorn 0.34.0, SQLAlchemy 2.0.36, Pydantic 2.10.4, SQLite, Pytest 8.3.4, HTTPX 0.27.2 (used by the test client), Git and GitHub.

## Architecture
```
Client (Swagger UI / curl)
   -> routes (app/routes/*.py): HTTP only - read the request, return the response
   -> schemas (app/schemas.py): validate input, shape output
   -> services (app/services.py): ALL business rules (availability, overdue, borrow, return)
   -> models + database (app/models.py, app/database.py): SQLite via SQLAlchemy
```
`app/services.py` is a small addition to the suggested structure; it keeps the business logic in one place so the route files do not repeat it.

## Folder structure
```
lending-api/
├── app/
│   ├── __init__.py
│   ├── main.py          # creates the app, registers routes and error handlers
│   ├── database.py      # engine, sessions, foreign keys switched on
│   ├── models.py        # Book and Loan tables
│   ├── schemas.py       # request/response validation
│   ├── services.py      # business logic
│   └── routes/ (books.py, loans.py, overdue.py)
├── database/seed.py     # creates B1, B2, B3 (safe to re-run)
├── tests/ (conftest.py, test_books.py, test_loans.py, test_overdue.py)
├── docs/ (domain_diagram.md, api_route_plan.md, manual_test_examples.md, evidence_log.md, windows_setup_and_submission_guide.md)
├── requirements.txt  pytest.ini  README.md  .gitignore  .env.example
```

## Database design
**books**: `id` (text, primary key), `title` (unique), `total_copies` (>= 0)
**loans**: `id` (auto number, primary key), `book_id` (foreign key to books.id), `borrower_alias`, `checkout_day` (>= 0), `due_day` (> checkout_day), `returned` (true/false, default false)
Indexes: `loans(book_id, returned)` and `loans(returned, due_day)`.

## Database rules
1. **Available copies = total copies - active loans** (active = `returned = false`). There is no `available` column.
2. **Overdue only when `current_day > due_day` AND `returned = false`.** Due day 10: not overdue on day 10, overdue on day 11. There is no `is_overdue` column.
3. Borrowers are fictional aliases (letters, digits, `_`, `-`). No names, e-mails, phone numbers or student numbers.
4. Invalid input is rejected (HTTP 422) before any database change.
5. The availability check and the insert of a new loan happen in one atomic SQL statement, so availability can never go negative.

## Installation (Windows, VS Code)
Full beginner steps are in [`docs/windows_setup_and_submission_guide.md`](docs/windows_setup_and_submission_guide.md). In short, from the project folder:
```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```
PowerShell users: if activation is blocked, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` first, or use the Command Prompt (cmd).

## Environment setup
No configuration is needed. Optionally set `DATABASE_URL` (see `.env.example`) to use another SQLite file. The app reads it from the environment; it does not load `.env` files.

## Database initialization and seed
```
python -m database.seed
```
Creates the tables and the three books (B1 Python Basics x2, B2 Design Notes x1, B3 Data Stories x3 = 6 copies), then validates them. Running it again creates nothing new. To start completely fresh, stop the server and delete `lending.db`.

## Run the application
```
python -m uvicorn app.main:app --reload
```
Swagger UI: **http://127.0.0.1:8000/docs** (ReDoc: http://127.0.0.1:8000/redoc).

## API endpoints
| Method | Path | Purpose | Status codes |
|---|---|---|---|
| GET | `/books/` | List books, optional `?search=` | 200 |
| GET | `/books/{book_id}` | Book details | 200, 404 |
| POST | `/loans/` | Borrow a book | 201, 404, 409, 422 |
| POST | `/loans/{loan_id}/return` | Return a book | 200, 404, 409 |
| GET | `/overdue/?current_day=N` | Overdue loans on day N | 200, 422 |

## Examples
Borrow: `POST /loans/`
```json
{"book_id": "B1", "borrower_alias": "finch", "checkout_day": 3}
```
Response `201`:
```json
{"id": 1, "book_id": "B1", "borrower_alias": "finch", "checkout_day": 3, "due_day": 10, "returned": false}
```
Overdue: `GET /overdue/?current_day=11` returns `[]` if nothing is late, or items like
```json
{"loan_id": 1, "book_id": "B1", "book_title": "Python Basics", "borrower_alias": "finch", "checkout_day": 3, "due_day": 10, "current_day": 11, "overdue": true}
```
More expected examples: `docs/manual_test_examples.md`.

## Testing
```
pytest -v
```
Each test uses its own temporary database, so `lending.db` is never touched. Real results you captured belong in `docs/evidence_log.md`.

## Assumptions and known limitations
- Design choices not fixed by the brief are listed in `docs/api_route_plan.md`.
- There are no user accounts or authentication; anyone can call any endpoint.
- Days are plain whole numbers (day 1, 2, 3 ...), not calendar dates.
- A loan record cannot be edited or deleted through the API.
- SQLite allows one writer at a time; this is fine for a small library but not for heavy traffic.
- The app is designed to run locally and is not deployed to a public host.

## AI assistance disclosure
This project's code, tests and documentation were generated with the help of Claude (an AI assistant made by Anthropic) and then reviewed by the author. [Edit this section: state honestly what you checked, ran and changed yourself.]
