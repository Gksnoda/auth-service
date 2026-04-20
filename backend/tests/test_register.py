from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def _mock_supabase_insert(mock_supabase):
    mock_table = MagicMock()
    mock_supabase.table.return_value = mock_table
    mock_table.insert.return_value = mock_table
    mock_table.execute.return_value = MagicMock()
    return mock_table


@patch("main.supabase")
def test_register_ok(mock_supabase):
    _mock_supabase_insert(mock_supabase)

    response = client.post("/auth/register", json={
        "email": "test@example.com",
        "password": "validpass",
        "name": "Test User",
    })

    assert response.status_code == 201


@patch("main.supabase")
def test_register_duplicate_email(mock_supabase):
    mock_table = _mock_supabase_insert(mock_supabase)
    mock_table.execute.side_effect = Exception("duplicate key value violates unique constraint")

    response = client.post("/auth/register", json={
        "email": "existing@example.com",
        "password": "validpass",
        "name": "Test User",
    })

    assert response.status_code == 409
    assert "already exists" in response.json()["detail"].lower()


def test_register_invalid_email():
    response = client.post("/auth/register", json={
        "email": "not-an-email",
        "password": "validpass",
        "name": "Test User",
    })

    assert response.status_code == 422


def test_register_password_too_short():
    response = client.post("/auth/register", json={
        "email": "test@example.com",
        "password": "1234",
        "name": "Test User",
    })

    assert response.status_code == 422


def test_register_password_too_long():
    response = client.post("/auth/register", json={
        "email": "test@example.com",
        "password": "a" * 51,
        "name": "Test User",
    })

    assert response.status_code == 422
