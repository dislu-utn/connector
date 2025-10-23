from typing import Literal, Dict, Any
from pydantic import BaseModel


class IntegrateDTO(BaseModel):
    institution_id: str
    origin: str #dislu or adaptaria
    payload: Dict[str, Any]
    endpoint: str #The endpoint used
    method: Literal["", "post", "get"] #
