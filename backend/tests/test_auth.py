from app.core.security import create_access_token, decode_access_token, hash_password, verify_password


def test_password_hash_is_not_plain_text():
    hashed = hash_password("strong-password")
    assert hashed != "strong-password"
    assert verify_password("strong-password", hashed)


def test_access_token_round_trip():
    assert decode_access_token(create_access_token("42")) == "42"
