from pydantic import BaseModel

class Product(BaseModel):
    id: int
    name: str
    cost: int
    category: str
    img: str