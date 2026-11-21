# Domain Diagram

## Entities and relationship

```
┌────────────────────┐        1        0..*   ┌──────────────────────┐
│       books        │───────────────────────▶│        loans         │
├────────────────────┤  "a book has many      ├──────────────────────┤
│ PK id (B1,B2,B3)   │   loans over time"     │ PK id                │
│    title           │                        │ FK book_id → books.id│
│    total_copies    │                        │    borrower_alias    │
└────────────────────┘                        │    checkout_day      │
                                              │    due_day           │
                                              │    returned          │
                                              └──────────────────────┘
```

## Books, copies and loans

Physical copies are not separate rows. A book stores `total_copies`; each ACTIVE loan occupies one copy.

```
B1 Python Basics   total_copies = 2     [copy][copy]
B2 Design Notes    total_copies = 1     [copy]
B3 Data Stories    total_copies = 3     [copy][copy][copy]      -> 6 physical copies

Active loan   (returned = false) --occupies--> one copy of its book
Returned loan (returned = true)  --frees-----> that copy
```

## Stored versus derived

| Value | Stored or derived | How |
|---|---|---|
| `books.id`, `books.title`, `books.total_copies` | Stored | Written by the seed script |
| `loans.id`, `book_id`, `borrower_alias`, `checkout_day`, `due_day`, `returned` | Stored | Written by `POST /loans/` and `POST /loans/{id}/return` |
| `due_day` | Stored at borrow time | `checkout_day + 7`, calculated once by the API |
| **Available copies** | **Derived** | `total_copies - COUNT(loans WHERE book_id = X AND returned = false)` on every request |
| **Overdue status** | **Derived** | `current_day > due_day AND returned = false` on every report request |

There is no `available` column and no `is_overdue` column anywhere in the schema.

## Overdue timeline example (checkout day 3, due day 10)

```
day:      3        9        10        11
          |--------|--------|---------|
       checkout          due day    overdue (if not returned)
                         NOT overdue
```
