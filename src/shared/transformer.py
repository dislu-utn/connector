from abc import abstractmethod
from typing import Literal, Optional, Dict, Any
from dataclasses import dataclass

class Transformer():

    @abstractmethod
    def run(self, endpoint:str, method:str, payload: Dict[str, Any]):
        pass

@dataclass
class TransformedRequest:
    url: str
    method: Optional[Literal["post", "get"]]
    payload: Dict[str, Any]
