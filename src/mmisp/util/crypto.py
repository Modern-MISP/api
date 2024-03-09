from passlib.context import CryptContext


def verify_secret(secret: str, secret_hash: str) -> bool:
    context = CryptContext(schemes=["argon2", "bcrypt"])
    return context.verify(secret, secret_hash)


def hash_secret(secret: str) -> str:
    context = CryptContext(schemes=["argon2", "bcrypt"])
    return context.hash(secret)
