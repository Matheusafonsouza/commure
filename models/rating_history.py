from typing import List
from pydantic import BaseModel


class RatingHistory(BaseModel):
    name: str
    points: List[List[int]]
