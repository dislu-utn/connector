from abc import abstractmethod
from typing import Literal, Optional, Dict, Any, TypedDict
from dataclasses import dataclass

class Transformer():

    @abstractmethod
    def run(self, endpoint:str, method:str, payload: TypedDict):
        pass

@dataclass
class TransformedRequest:
    url: str
    method: Optional[Literal["post", "get"]]
    payload: Dict[str, Any]
