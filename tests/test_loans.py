"""Borrow and return tests (cases 8-22 of the brief, plus extras)."""
from sqlalchemy import func, select

from app.models import Loan


def borrow(client, book_id="B1", alias="finch", day=3):
    return client.post(
        "/loans/", json={"book_id": book_id, "borrower_alias": alias, "checkout_day": day}
    )


def available(client, book_id):
    return client.get(f"/books/{book_id}").json()["available_copies"]


def count_loans(session_factory, active_only=False):
    with session_factory() as db:
        stmt = select(func.count(Loan.id))
        if active_only:
            stmt = stmt.where(Loan.returned.is_(False))
        return db.scalar(stmt)


# ------------------------------------------------------------- borrowing ----
def test_08_successfully_borrow_a_book(client):
    response = borrow(client)
    assert response.status_code == 201
    body = response.json()
    assert body["book_id"] == "B1"
    assert body["borrower_alias"] == "finch"
    assert body["checkout_day"] == 3
    assert body["returned"] is False


def test_09_due_day_is_checkout_day_plus_7(client):
    assert borrow(client, day=3).json()["due_day"] == 10
    assert borrow(client, alias="wren", day=20).json()["due_day"] == 27


def test_10_borrow_second_copy_of_b1(client):
    assert borrow(client, alias="finch").status_code == 201
    assert borrow(client, alias="wren").status_code == 201


def test_11_reject_b1_when_both_copies_borrowed(client):
    borrow(client, alias="finch")
    borrow(client, alias="wren")
    response = borrow(client, alias="lark")
    assert response.status_code == 409
    assert "available" in response.json()["detail"]


def test_12_reject_b2_when_only_copy_borrowed(client):
    assert borrow(client, book_id="B2").status_code == 201
    assert borrow(client, book_id="B2", alias="wren").status_code == 409


def test_13_reject_unknown_book_id(client):
    response = borrow(client, book_id="B99")
    assert response.status_code == 404
    assert "B99" in response.json()["detail"]


def test_14_reject_empty_borrower_alias(client):
    assert borrow(client, alias="").status_code == 422


def test_15_reject_missing_borrower_alias(client):
    response = client.post("/loans/", json={"book_id": "B1", "checkout_day": 3})
    assert response.status_code == 422


def test_16_failed_requests_do_not_create_loan_records(client, session_factory):
    borrow(client, book_id="B2")  # takes the only copy: 1 loan exists
    assert count_loans(session_factory) == 1

    assert borrow(client, book_id="B2", alias="wren").status_code == 409   # no copies
    assert borrow(client, book_id="B99").status_code == 404                # unknown book
    assert borrow(client, alias="").status_code == 422                     # empty alias
    assert borrow(client, day=-1).status_code == 422                       # bad day
    assert client.post("/loans/", json={"book_id": "B1", "checkout_day": 3}).status_code == 422

    assert count_loans(session_factory) == 1  # still only the first loan


def test_17_availability_decreases_after_successful_loan(client):
    assert available(client, "B1") == 2
    borrow(client)
    assert available(client, "B1") == 1
    borrow(client, alias="wren")
    assert available(client, "B1") == 0
    assert available(client, "B3") == 3  # other books are unaffected


def test_extra_invalid_checkout_day_rejected(client):
    assert borrow(client, day=-5).status_code == 422
    response = client.post(
        "/loans/", json={"book_id": "B1", "borrower_alias": "finch", "checkout_day": "three"}
    )
    assert response.status_code == 422


def test_extra_personal_data_is_rejected(client):
    assert borrow(client, alias="jane@example.com").status_code == 422
    response = client.post(
        "/loans/",
        json={"book_id": "B1", "borrower_alias": "finch", "checkout_day": 3, "email": "a@b.com"},
    )
    assert response.status_code == 422


# ------------------------------------------------------------- returning ----
def test_18_successfully_return_an_active_loan(client):
    loan_id = borrow(client).json()["id"]
    response = client.post(f"/loans/{loan_id}/return")
    assert response.status_code == 200
    assert response.json()["returned"] is True


def test_19_availability_increases_after_return(client):
    loan_id = borrow(client).json()["id"]
    assert available(client, "B1") == 1
    client.post(f"/loans/{loan_id}/return")
    assert available(client, "B1") == 2


def test_20_reject_returning_the_same_loan_twice(client):
    loan_id = borrow(client).json()["id"]
    assert client.post(f"/loans/{loan_id}/return").status_code == 200
    second = client.post(f"/loans/{loan_id}/return")
    assert second.status_code == 409
    assert "already been returned" in second.json()["detail"]
    assert available(client, "B1") == 2  # the duplicate did not change availability


def test_21_reject_unknown_loan_id(client):
    response = client.post("/loans/9999/return")
    assert response.status_code == 404
    assert "9999" in response.json()["detail"]


def test_22_returned_loans_are_no_longer_active(client, session_factory):
    loan_id = borrow(client).json()["id"]
    assert count_loans(session_factory, active_only=True) == 1
    client.post(f"/loans/{loan_id}/return")
    assert count_loans(session_factory, active_only=True) == 0
    assert count_loans(session_factory) == 1  # the loan record itself is kept


# ------------------------------------------- one active loan per alias/title ----
def test_extra_same_alias_cannot_hold_two_copies_of_same_title(client, session_factory):
    assert borrow(client, alias="finch").status_code == 201
    second = borrow(client, alias="finch")
    assert second.status_code == 409
    assert "already has an active loan" in second.json()["detail"]
    assert count_loans(session_factory) == 1
    assert available(client, "B1") == 1


def test_extra_same_alias_can_borrow_again_after_returning(client):
    loan_id = borrow(client, alias="finch").json()["id"]
    client.post(f"/loans/{loan_id}/return")
    assert borrow(client, alias="finch").status_code == 201


def test_extra_same_alias_can_borrow_different_titles(client):
    assert borrow(client, book_id="B1", alias="finch").status_code == 201
    assert borrow(client, book_id="B3", alias="finch").status_code == 201
