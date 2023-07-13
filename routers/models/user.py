from pydantic import BaseModel
from .product import Product

class User(BaseModel):
    email: str
    points: int
    redeemHistory: list
    challengeHistory: list
    badges: list