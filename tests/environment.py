def auth_header(token: str) -> dict:
    return {"authorization": f"Bearer {token}"}
