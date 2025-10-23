from abc import ABC, abstractmethod
from typing import TypedDict
import requests
from src.shared.integrate_dto import IntegrateDTO
from src.shared.transformer import TransformedRequest

class Provider(ABC):
    
    @abstractmethod
    def transform(self, endpoint:str, method:str, payload: TypedDict) -> TransformedRequest:
        pass

    def sync(self, message: IntegrateDTO):
        transformed_request = self.transform(endpoint=message.endpoint, method=message.method, payload=message.payload)

        if transformed_request.method == "post":
            requests.post(url= transformed_request.url, json=transformed_request.payload)
        """
        SEGUIR Y TESTEAR ESTO
        """
        
        pass
