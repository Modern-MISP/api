from passlib.context import CryptContext


def verify_password(pw: str, pw_hash: str) -> bool:
    context = CryptContext(schemes=["argon2", "bcrypt"])
    return context.verify(pw, pw_hash)


def hash_password(pw: str) -> str:
    context = CryptContext(schemes=["argon2", "bcrypt"])
    return context.hash(pw)
