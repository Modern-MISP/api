import hashlib
import hmac


def create_hash(secret_key: str, value: str) -> str:
    hmac_object = hmac.new(secret_key.encode(), value.encode(), hashlib.sha256)
    return hmac_object.hexdigest()
