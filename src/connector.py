from typing import Literal, TypedDict
from src.shared.integrate_dto import IntegrateDTO
from src.shared.transformer import TransformedRequest
from src.adaptaria.provider.adaptaria_provider import AdaptariaProvider
from src.dislu.provider.dislu_provider import DisluProvider


class Connector():

    def __init__(self, origin: Literal["dislu", "adaptaria"]):
        self.origin = origin
        
        if origin == "dislu":
            self.provider = DisluProvider()
        elif origin == "adaptaria":
            self.provider = AdaptariaProvider()
        else:
            raise Exception("Invalid origin")
    
    def integrate(self, message: IntegrateDTO) -> bool: 
        """
        - Busco los servicios en la db a los que me tengo que integrar
        - Fijarme en la base de datos si esta ok la suscripcion a ambos servicios
        """
        self.provider.initialize(message)
        self.provider.sync(endpoint=message.endpoint, method=message.method, payload=message.payload)
        # Send the request
        return True
