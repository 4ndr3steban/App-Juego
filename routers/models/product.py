from pydantic import BaseModel

class Product(BaseModel):
    name: str
    cost: int
    category: str
    img: str