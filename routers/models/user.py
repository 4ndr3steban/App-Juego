from pydantic import BaseModel
from .product import Product
from .challenge import Challenge

class User(BaseModel):
    email: str
    points: int
    redeemHistory: list[tuple]
    challengeHistory: list[tuple]
    badges: list[int]