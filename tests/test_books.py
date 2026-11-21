"""Book endpoint tests (cases 1-7 of the brief, plus two extras)."""


def test_01_list_all_three_books(client):
    response = client.get("/books/")
    assert response.status_code == 200
    books = response.json()
    assert [b["id"] for b in books] == ["B1", "B2", "B3"]
    assert [b["title"] for b in books] == ["Python Basics", "Design Notes", "Data Stories"]


def test_02_total_copies(client):
    books = {b["id"]: b for b in client.get("/books/").json()}
    assert books["B1"]["total_copies"] == 2
    assert books["B2"]["total_copies"] == 1
    assert books["B3"]["total_copies"] == 3
    assert sum(b["total_copies"] for b in books.values()) == 6


def test_03_initial_available_copies_equal_total(client):
    for book in client.get("/books/").json():
        assert book["available_copies"] == book["total_copies"]


def test_04_search_by_title(client):
    response = client.get("/books/", params={"search": "python"})
    assert response.status_code == 200
    assert [b["id"] for b in response.json()] == ["B1"]


def test_05_search_is_case_insensitive(client):
    for term in ("python", "PYTHON", "PyThOn"):
        response = client.get("/books/", params={"search": term})
        assert [b["id"] for b in response.json()] == ["B1"], term


def test_06_search_for_book_that_does_not_exist(client):
    response = client.get("/books/", params={"search": "zzz-no-such-book"})
    assert response.status_code == 200
    assert response.json() == []


def test_07_invalid_book_id_returns_404(client):
    response = client.get("/books/B99")
    assert response.status_code == 404
    assert "B99" in response.json()["detail"]


def test_extra_get_single_book(client):
    response = client.get("/books/B3")
    assert response.status_code == 200
    assert response.json() == {
        "id": "B3", "title": "Data Stories", "total_copies": 3, "available_copies": 3,
    }


def test_extra_search_wildcard_characters_are_literal(client):
    assert client.get("/books/", params={"search": "%"}).json() == []
