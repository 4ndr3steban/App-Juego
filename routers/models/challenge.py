from pydantic import BaseModel

class Challenge(BaseModel):
    title: str
    cluster: str
    points: int
    image: str
    ismacro: bool
    exp_time: int
    form: str
    
    