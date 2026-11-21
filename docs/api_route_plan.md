# API Route Plan

| Method and path | Purpose | Success | Error responses |
|---|---|---|---|
| `GET /books/` | List all books (id, title, total_copies, available_copies) | 200 | none |
| `GET /books/?search=python` | Case-insensitive title search | 200 (empty list if no match) | none |
| `GET /books/{book_id}` | One book | 200 | 404 unknown book |
| `POST /loans/` | Borrow a book; `due_day = checkout_day + 7` | 201 | 404 unknown book, 409 no copies, 422 invalid alias or day |
| `POST /loans/{loan_id}/return` | Return a loan | 200 | 404 unknown loan, 409 already returned |
| `GET /overdue/?current_day=11` | Overdue loans on the given day | 200 | 422 missing or invalid `current_day` |

## Order of checks in `POST /loans/`
1. Pydantic validates the body (422 on failure) - nothing touches the database.
2. The book is looked up (404 if missing).
3. One atomic `INSERT ... SELECT ... WHERE available > 0` creates the loan; if no row is inserted the API answers 409.

## Error format
All errors from our code: `{"detail": "readable message"}`. Validation errors (422) use FastAPI's standard body with a `detail` list.

## Assumptions (the brief does not specify these)
1. `book_id` is a string such as `"B1"`; `loan_id` is an auto-increment integer.
2. Alias: 1-30 characters, letters, digits, `_` and `-` only; surrounding spaces are trimmed. Extra fields in the body are rejected.
3. `checkout_day` and `current_day` are whole numbers from 0 to 1,000,000 (strict integers, not strings).
4. The 7-day loan period is a constant in `app/services.py`.
5. Search is a "contains" match; an empty search returns all books.
6. `POST /loans/` returns 201; the return endpoint returns 200 with the updated loan.
7. `current_day` is required on `/overdue/`.
8. Book titles are unique. The same alias may borrow the same book more than once.
9. Concurrency is handled by a single atomic SQL statement (SQLite allows one writer at a time).
