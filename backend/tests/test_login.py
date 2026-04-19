from unittest.mock import patch, MagicMock

from argon2.exceptions import VerifyMismatchError
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def _mock_supabase_select(mock_supabase, data=None):
    mock_chain = MagicMock()
    mock_supabase.table.return_value = mock_chain
    mock_chain.select.return_value = mock_chain
    mock_chain.eq.return_value = mock_chain
    mock_chain.execute.return_value = MagicMock(data=data or [])
    return mock_chain


@patch("main.ph")
@patch("main.supabase")
def test_login_ok(mock_supabase, mock_ph):
    _mock_supabase_select(mock_supabase, data=[{
        "email": "test@example.com",
        "password_hash": "stored-hash",
        "name": "Test User",
    }])
    mock_ph.verify.return_value = True

    response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "validpass",
    })

    assert response.status_code == 200


@patch("main.ph")
@patch("main.supabase")
def test_login_user_not_found(mock_supabase, mock_ph):
    _mock_supabase_select(mock_supabase, data=[])

    response = client.post("/auth/login", json={
        "email": "nobody@example.com",
        "password": "whatever",
    })

    assert response.status_code == 401
    # Timing-attack protection: ph.verify must run even when the user does not
    # exist, so both branches take the same time.
    mock_ph.verify.assert_called_once()


@patch("main.ph")
@patch("main.supabase")
def test_login_wrong_password(mock_supabase, mock_ph):
    _mock_supabase_select(mock_supabase, data=[{
        "email": "test@example.com",
        "password_hash": "stored-hash",
    }])
    mock_ph.verify.side_effect = VerifyMismatchError()

    response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "wrongpass",
    })

    assert response.status_code == 401


@patch("main.ph")
@patch("main.supabase")
def test_login_same_error_for_user_not_found_and_wrong_password(mock_supabase, mock_ph):
    # Case 1: wrong password
    _mock_supabase_select(mock_supabase, data=[{
        "email": "test@example.com",
        "password_hash": "stored-hash",
    }])
    mock_ph.verify.side_effect = VerifyMismatchError()
    resp_wrong_pw = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "wrongpass",
    })

    # Case 2: user not found
    _mock_supabase_select(mock_supabase, data=[])
    mock_ph.verify.side_effect = None
    resp_not_found = client.post("/auth/login", json={
        "email": "nobody@example.com",
        "password": "whatever",
    })

    assert resp_wrong_pw.status_code == resp_not_found.status_code == 401
    assert resp_wrong_pw.json() == resp_not_found.json()


def test_login_invalid_email():
    response = client.post("/auth/login", json={
        "email": "not-an-email",
        "password": "whatever",
    })

    assert response.status_code == 422


def test_login_missing_email():
    response = client.post("/auth/login", json={
        "password": "whatever",
    })

    assert response.status_code == 422


def test_login_missing_password():
    response = client.post("/auth/login", json={
        "email": "test@example.com",
    })

    assert response.status_code == 422
