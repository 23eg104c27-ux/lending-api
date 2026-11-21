"""Overdue report tests (cases 23-28 of the brief)."""


def borrow(client, book_id="B1", alias="finch", day=3):
    return client.post(
        "/loans/", json={"book_id": book_id, "borrower_alias": alias, "checkout_day": day}
    )


def overdue(client, day):
    return client.get("/overdue/", params={"current_day": day})


def test_23_loan_is_not_overdue_on_its_due_day(client):
    borrow(client, day=3)  # due_day = 10
    response = overdue(client, 10)
    assert response.status_code == 200
    assert response.json() == []


def test_24_loan_is_overdue_one_day_after_due_day(client):
    borrow(client, day=3)  # due_day = 10
    response = overdue(client, 11)
    assert response.status_code == 200
    report = response.json()
    assert len(report) == 1
    assert report[0]["overdue"] is True


def test_25_returned_loans_are_not_overdue(client):
    loan_id = borrow(client, day=3).json()["id"]
    assert len(overdue(client, 11).json()) == 1
    client.post(f"/loans/{loan_id}/return")
    assert overdue(client, 11).json() == []


def test_26_loans_not_yet_due_are_excluded(client):
    borrow(client, day=3)  # due_day = 10
    assert overdue(client, 5).json() == []
    assert overdue(client, 0).json() == []


def test_27_current_day_parameter_controls_the_result(client):
    borrow(client, day=3)  # due_day = 10
    assert overdue(client, 9).json() == []
    assert overdue(client, 10).json() == []
    assert len(overdue(client, 11).json()) == 1
    assert len(overdue(client, 500).json()) == 1
    # current_day is required and must be a non-negative integer
    assert client.get("/overdue/").status_code == 422
    assert overdue(client, -1).status_code == 422
    assert client.get("/overdue/", params={"current_day": "abc"}).status_code == 422


def test_28_report_contains_correct_book_and_borrower_details(client):
    loan_id = borrow(client, book_id="B2", alias="wren", day=3).json()["id"]
    borrow(client, book_id="B1", alias="finch", day=20)  # due 27: not overdue on day 11
    report = overdue(client, 11).json()
    assert report == [
        {
            "loan_id": loan_id,
            "book_id": "B2",
            "book_title": "Design Notes",
            "borrower_alias": "wren",
            "checkout_day": 3,
            "due_day": 10,
            "current_day": 11,
            "overdue": True,
        }
    ]
