from abc import abstractmethod
from typing import Literal, Optional, Dict, Any, TypedDict
from dataclasses import dataclass

import requests

from src.to_adaptaria.utils.endpoints import AdaptariaAPI
from src.to_dislu.utils.endpoints import DisluAPI

class Transformer():
    adaptaria_api = AdaptariaAPI()
    dislu_api = DisluAPI()

    def __init__(self, institution_id) -> None:
        self.institution_id = institution_id

    @abstractmethod
    def run(self, endpoint:str, method:str, payload: TypedDict):
        pass
    @abstractmethod
    def create(self, entity_id:str, endpoint: str):
        pass
    @abstractmethod
    def update(self, entity_id:str, endpoint: str):
        pass
    
@dataclass
class TransformedRequest:
    url: str
    method: Optional[Literal["post", "get"]]
    payload: Dict[str, Any]
