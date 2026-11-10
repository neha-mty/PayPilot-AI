"""Unit tests for authentication service."""
from app.services.auth_service import hash_password, verify_password, create_access_token
from jose import jwt
from app.config import get_settings

settings = get_settings()


def test_password_hashing_and_verification():
    raw_password = "SecurePassword123!"
    hashed = hash_password(raw_password)

    assert hashed != raw_password
    assert verify_password(raw_password, hashed) is True
    assert verify_password("WrongPassword!", hashed) is False


def test_jwt_token_generation_and_decoding():
    user_id = "test-user-uuid-1234"
    token = create_access_token(user_id)

    assert isinstance(token, str)
    decoded = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    assert decoded["sub"] == user_id
    assert "exp" in decoded
