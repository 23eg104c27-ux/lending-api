# Manual Test Examples - EXPECTED results (not captured evidence)

> These are what you SHOULD see if you follow the steps on a freshly seeded database
> (delete `lending.db`, run `python -m database.seed`, start the server).
> Real captured evidence goes in `docs/evidence_log.md` only after you run them yourself.
> Loan ids assume a fresh database (the first loan is id 1).

## Run in this order

| # | Request | Expected status | Expected body |
|---|---|---|---|
| 1 | `GET /books/` | 200 | three books, `available_copies` = 2, 1, 3 |
| 2 | `GET /books/?search=python` | 200 | `[{"id":"B1","title":"Python Basics","total_copies":2,"available_copies":2}]` |
| 3 | `GET /books/B1` | 200 | `{"id":"B1","title":"Python Basics","total_copies":2,"available_copies":2}` |
| 4 | `POST /loans/` `{"book_id":"B1","borrower_alias":"finch","checkout_day":3}` | 201 | `{"id":1,"book_id":"B1","borrower_alias":"finch","checkout_day":3,"due_day":10,"returned":false}` |
| 5 | `POST /loans/` `{"book_id":"B2","borrower_alias":"wren","checkout_day":3}` | 201 | loan id 2, `due_day` 10 |
| 6 | `POST /loans/` `{"book_id":"B2","borrower_alias":"lark","checkout_day":4}` | 409 | `{"detail":"No copies of 'Design Notes' are currently available."}` |
| 7 | `POST /loans/` `{"book_id":"B9","borrower_alias":"lark","checkout_day":4}` | 404 | `{"detail":"Book 'B9' not found."}` |
| 8 | `POST /loans/1/return` | 200 | loan 1 with `"returned": true` |
| 9 | `POST /loans/1/return` (again) | 409 | `{"detail":"Loan 1 has already been returned."}` |
| 10 | `GET /overdue/?current_day=10` (loan 2 is due on day 10) | 200 | `[]` |
| 11 | `GET /overdue/?current_day=11` | 200 | one item: loan 2, `book_title` "Design Notes", `borrower_alias` "wren", `checkout_day` 3, `due_day` 10, `current_day` 11, `overdue` true (loan 1 is not listed because it was returned) |
| 12 | `POST /loans/2/return`, then `GET /overdue/?current_day=11` | 200 | `[]` |

Invalid input: `POST /loans/` with `"borrower_alias": ""` returns 422.
