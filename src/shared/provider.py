from abc import ABC, abstractmethod
from typing import TypedDict
import requests
from src.shared.integrate_dto import IntegrateDTO
from src.shared.transformer import TransformedRequest

class Provider(ABC):

    def initialize(self, message:IntegrateDTO):
        self.institution_id = message.institution_id
        self.entity = message.entity
        self.entity_id = message.entity_id
        self.method = message.method

    @abstractmethod
    def transform(self) -> TransformedRequest:
        pass

    def provide(self, request: TransformedRequest) -> requests.Response | None:
        method = request.method.lower()
        if method == "post":
            response = requests.post(url=request.url, json=request.payload)
        elif method == "patch":
            response = requests.patch(url=request.url, json=request.payload)
        elif method == "get":
            response = requests.get(url=request.url, params=request.payload)
        elif method == "put":
            response = requests.put(url=request.url, json=request.payload)
        elif method == "delete":
            response = requests.delete(url=request.url, json=request.payload)
        else:
            return None

        if not response.ok:
            raise Exception(f"HTTP request failed with status code {response.status_code}: {response.text}")

        return response


    def sync(self):
        #TODO: Ver tema de external reference
        transformed_request = self.transform()
        return self.provide(transformed_request)

        """
        SEGUIR Y TESTEAR ESTO
        """
        
        pass
