import hashlib
import hmac
import secrets


def generate_link_token() -> str:
    return secrets.token_urlsafe(32)


def hash_token(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode()).hexdigest()


def verify_token(raw_token: str, stored_hash: str | None) -> bool:
    if not stored_hash:
        return False
    return hmac.compare_digest(hash_token(raw_token), stored_hash)
