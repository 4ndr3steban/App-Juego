from pydantic import BaseModel

class microChallenge(BaseModel):
    id: int
    category: str
    points: int
    completed: bool
    name: str
    icon: str
    bg_color: str
    
    