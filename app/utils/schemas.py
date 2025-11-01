from pydantic import BaseModel


class StatSchema(BaseModel):
    count: int = 0
    total: int = 0
