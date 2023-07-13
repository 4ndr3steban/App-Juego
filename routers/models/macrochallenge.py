from pydantic import BaseModel

class macroChallenge(BaseModel):
    id: int
    category: str
    points: int
    completed: bool
    name: str
    image: str
    bg_color: str
    time: str
    forms: str