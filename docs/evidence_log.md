# Evidence Log

Fill this in YOURSELF after running each step. Do not write results you have not actually seen.
Status values: NOT YET CAPTURED / CAPTURED.

| # | Evidence | How to produce it | Screenshot filename | Status | Date captured |
|---|---|---|---|---|---|
| 1 | Seed output (3 books, validation OK) | `python -m database.seed` | `01_seed_output.png` | NOT YET CAPTURED | |
| 2 | Swagger UI home page | open http://127.0.0.1:8000/docs | `02_swagger_home.png` | NOT YET CAPTURED | |
| 3 | List books (200) | `GET /books/` | `03_list_books_200.png` | NOT YET CAPTURED | |
| 4 | Search "python" (200) | `GET /books/?search=python` | `04_search_python_200.png` | NOT YET CAPTURED | |
| 5 | Book detail (200) | `GET /books/B1` | `05_book_b1_200.png` | NOT YET CAPTURED | |
| 6 | Unknown book (404) | `GET /books/B99` | `06_book_unknown_404.png` | NOT YET CAPTURED | |
| 7 | Borrow success (201) | `POST /loans/` finch / B1 / day 3 | `07_borrow_success_201.png` | NOT YET CAPTURED | |
| 8 | Borrow, no copies (409) | borrow B2 twice | `08_borrow_no_copies_409.png` | NOT YET CAPTURED | |
| 9 | Borrow unknown book (404) | `POST /loans/` with B9 | `09_borrow_unknown_book_404.png` | NOT YET CAPTURED | |
| 10 | Borrow empty alias (422) | `POST /loans/` with alias "" | `10_borrow_empty_alias_422.png` | NOT YET CAPTURED | |
| 11 | Return success (200) | `POST /loans/1/return` | `11_return_success_200.png` | NOT YET CAPTURED | |
| 12 | Return twice (409) | repeat the return | `12_return_twice_409.png` | NOT YET CAPTURED | |
| 13 | Overdue on due day (empty) | `GET /overdue/?current_day=10` | `13_overdue_due_day_empty.png` | NOT YET CAPTURED | |
| 14 | Overdue after due day | `GET /overdue/?current_day=11` | `14_overdue_after_due_day.png` | NOT YET CAPTURED | |
| 15 | Overdue after return (empty) | return the loan, repeat day 11 | `15_overdue_after_return_empty.png` | NOT YET CAPTURED | |
| 16 | Automated tests | `pytest -v` | `16_pytest_results.png` | NOT YET CAPTURED | |
| 17 | GitHub repository page | after upload | `17_github_repo.png` | NOT YET CAPTURED | |

## Automated test result (paste the real summary line here after running `pytest -v`)
```
(not yet run on your computer)
```
