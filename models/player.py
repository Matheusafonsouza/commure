from pydantic import BaseModel


class Player(BaseModel):
    username: str
