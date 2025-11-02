from typing import Literal, Dict, Any
from pydantic import BaseModel


class IntegrateDTO(BaseModel):
    institution_id: str
    entity: str
    entity_id: str
    origin: str #dislu or adaptaria
    method: Literal["", "post", "get"] #
