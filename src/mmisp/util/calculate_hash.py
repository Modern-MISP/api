import hashlib


# This function generates a sha256 hash out of the input.
def calculate_sha256(input_str: str) -> str:
    sha256_hash = hashlib.sha256(input_str.encode("utf-8"))
    return sha256_hash.hexdigest()
