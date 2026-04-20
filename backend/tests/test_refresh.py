from datetime import datetime, timedelta, timezone
from unittest.mock import patch, MagicMock

import jwt
from fastapi.testclient import TestClient

from main import JWT_ALGORITHM, JWT_SECRET, app

client = TestClient(app)


def _build_chain(data=None):
    chain = MagicMock()
    chain.select.return_value = chain
    chain.update.return_value = chain
    chain.insert.return_value = chain
    chain.eq.return_value = chain
    chain.execute.return_value = MagicMock(data=data or [])
    return chain


def _mock_supabase_by_table(mock_supabase, tables):
    chains = {name: _build_chain(data) for name, data in tables.items()}
    mock_supabase.table.side_effect = lambda name: chains[name]
    return chains


def _future_iso(days=7):
    return (datetime.now(timezone.utc) + timedelta(days=days)).isoformat()


def _past_iso(days=1):
    return (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()


def _valid_token_row(user_id="user-42", token_id="rt-1"):
    return {
        "id": token_id,
        "user_id": user_id,
        "token_hash": "irrelevant-hash",
        "expires_at": _future_iso(7),
        "revoked_at": None,
    }


def _user_row(user_id="user-42"):
    return {
        "id": user_id,
        "email": "test@example.com",
        "role": "user",
    }


@patch("main.supabase")
def test_refresh_returns_new_access_and_refresh_tokens(mock_supabase):
    _mock_supabase_by_table(mock_supabase, {
        "refresh_tokens": [_valid_token_row()],
        "users": [_user_row()],
    })

    response = client.post("/auth/refresh", json={"refresh_token": "any-raw-token"})

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body.get("access_token"), str) and body["access_token"]
    assert isinstance(body.get("refresh_token"), str) and body["refresh_token"]
    assert body.get("token_type") == "bearer"


@patch("main.supabase")
def test_refresh_access_token_has_expected_claims(mock_supabase):
    _mock_supabase_by_table(mock_supabase, {
        "refresh_tokens": [_valid_token_row()],
        "users": [_user_row()],
    })

    response = client.post("/auth/refresh", json={"refresh_token": "any-raw-token"})

    token = response.json()["access_token"]
    decoded = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])

    assert decoded["sub"] == "user-42"
    assert decoded["email"] == "test@example.com"
    assert decoded["role"] == "user"
    assert decoded["exp"] - decoded["iat"] == 15 * 60


@patch("main.supabase")
def test_refresh_rotates_token(mock_supabase):
    chains = _mock_supabase_by_table(mock_supabase, {
        "refresh_tokens": [_valid_token_row(token_id="rt-old")],
        "users": [_user_row()],
    })

    response = client.post("/auth/refresh", json={"refresh_token": "old-raw-token"})

    assert response.status_code == 200

    rt_chain = chains["refresh_tokens"]
    update_calls = rt_chain.update.call_args_list
    assert any(
        call.args
        and isinstance(call.args[0], dict)
        and "revoked_at" in call.args[0]
        for call in update_calls
    ), "expected the old refresh token to be revoked via update"

    insert_calls = rt_chain.insert.call_args_list
    assert any(
        call.args
        and isinstance(call.args[0], dict)
        and call.args[0].get("user_id") == "user-42"
        and call.args[0].get("token_hash")
        and call.args[0].get("expires_at")
        for call in insert_calls
    ), "expected a new refresh token to be inserted"


@patch("main.supabase")
def test_refresh_returns_different_refresh_token_than_input(mock_supabase):
    _mock_supabase_by_table(mock_supabase, {
        "refresh_tokens": [_valid_token_row()],
        "users": [_user_row()],
    })

    response = client.post("/auth/refresh", json={"refresh_token": "some-specific-token"})

    assert response.json()["refresh_token"] != "some-specific-token"


@patch("main.supabase")
def test_refresh_new_refresh_token_not_stored_in_plaintext(mock_supabase):
    chains = _mock_supabase_by_table(mock_supabase, {
        "refresh_tokens": [_valid_token_row()],
        "users": [_user_row()],
    })

    response = client.post("/auth/refresh", json={"refresh_token": "old-raw-token"})

    new_refresh_token = response.json()["refresh_token"]
    insert_calls = chains["refresh_tokens"].insert.call_args_list
    stored_hashes = [
        call.args[0]["token_hash"]
        for call in insert_calls
        if call.args and isinstance(call.args[0], dict) and "token_hash" in call.args[0]
    ]
    assert stored_hashes, "expected at least one insert with a token_hash"
    assert new_refresh_token not in stored_hashes


@patch("main.supabase")
def test_refresh_unknown_token_returns_401(mock_supabase):
    _mock_supabase_by_table(mock_supabase, {
        "refresh_tokens": [],
        "users": [],
    })

    response = client.post("/auth/refresh", json={"refresh_token": "unknown-token"})

    assert response.status_code == 401


@patch("main.supabase")
def test_refresh_revoked_token_returns_401(mock_supabase):
    revoked = _valid_token_row()
    revoked["revoked_at"] = _past_iso(1)

    _mock_supabase_by_table(mock_supabase, {
        "refresh_tokens": [revoked],
        "users": [_user_row()],
    })

    response = client.post("/auth/refresh", json={"refresh_token": "revoked-token"})

    assert response.status_code == 401


@patch("main.supabase")
def test_refresh_expired_token_returns_401(mock_supabase):
    expired = _valid_token_row()
    expired["expires_at"] = _past_iso(1)

    _mock_supabase_by_table(mock_supabase, {
        "refresh_tokens": [expired],
        "users": [_user_row()],
    })

    response = client.post("/auth/refresh", json={"refresh_token": "expired-token"})

    assert response.status_code == 401


@patch("main.supabase")
def test_refresh_revoked_token_is_not_rotated(mock_supabase):
    revoked = _valid_token_row()
    revoked["revoked_at"] = _past_iso(1)

    chains = _mock_supabase_by_table(mock_supabase, {
        "refresh_tokens": [revoked],
        "users": [_user_row()],
    })

    client.post("/auth/refresh", json={"refresh_token": "revoked-token"})

    insert_calls = chains["refresh_tokens"].insert.call_args_list
    assert not insert_calls, "a revoked refresh token must not trigger issuing a new one"


def test_refresh_same_error_for_different_invalid_states():
    def _post(mock_supabase, tables, body_token):
        _mock_supabase_by_table(mock_supabase, tables)
        return client.post("/auth/refresh", json={"refresh_token": body_token})

    with patch("main.supabase") as mock_supabase:
        resp_unknown = _post(mock_supabase, {
            "refresh_tokens": [],
            "users": [],
        }, "unknown")

    with patch("main.supabase") as mock_supabase:
        revoked = _valid_token_row()
        revoked["revoked_at"] = _past_iso(1)
        resp_revoked = _post(mock_supabase, {
            "refresh_tokens": [revoked],
            "users": [_user_row()],
        }, "revoked")

    with patch("main.supabase") as mock_supabase:
        expired = _valid_token_row()
        expired["expires_at"] = _past_iso(1)
        resp_expired = _post(mock_supabase, {
            "refresh_tokens": [expired],
            "users": [_user_row()],
        }, "expired")

    assert resp_unknown.status_code == resp_revoked.status_code == resp_expired.status_code == 401
    assert resp_unknown.json() == resp_revoked.json() == resp_expired.json()


def test_refresh_missing_refresh_token_returns_422():
    response = client.post("/auth/refresh", json={})
    assert response.status_code == 422
