from pydantic import BaseModel

class FilmClass(BaseModel):
    type_id: int
    type_pid: int
    type_name: str