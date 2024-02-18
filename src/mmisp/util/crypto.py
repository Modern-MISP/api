import hashlib

from passlib.context import CryptContext


def verify_password(pw: str, pw_hash: str) -> bool:
    context = CryptContext(schemes=["argon2", "bcrypt"])
    return context.verify(pw, pw_hash)


def hash_password(pw: str) -> str:
    context = CryptContext(schemes=["argon2", "bcrypt"])
    return context.hash(pw)


def hash_auth_key(key: str) -> str:
    sha256_hash = hashlib.sha256(key.encode("utf-8"))
    return sha256_hash.hexdigest()
