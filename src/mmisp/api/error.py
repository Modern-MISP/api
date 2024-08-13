from typing import Self


class LegacyMISPCompatibleHTTPException(Exception):
    def __init__(self: Self, status: int, message: str) -> None:
        self.status = status
        self.message = message
