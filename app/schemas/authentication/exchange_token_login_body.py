from pydantic import BaseModel


class ExchangeTokenLoginBody(BaseModel):
    exchangeToken: str
