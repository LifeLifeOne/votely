from datetime import UTC, datetime, timedelta

import jwt
from pwdlib import PasswordHash

ALGORITHM = "HS256"

# Argon2id with pwdlib's recommended parameters.
_password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return _password_hash.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return _password_hash.verify(password, hashed)


def create_access_token(subject: str, secret: str, ttl: timedelta) -> str:
    now = datetime.now(UTC)
    claims = {"sub": subject, "iat": now, "exp": now + ttl}
    return jwt.encode(claims, secret, algorithm=ALGORITHM)


def decode_access_token(token: str, secret: str) -> str | None:
    """Return the token subject, or None if the token is invalid or expired."""
    try:
        claims = jwt.decode(token, secret, algorithms=[ALGORITHM], options={"require": ["exp"]})
    except jwt.InvalidTokenError:
        return None
    return claims.get("sub")
