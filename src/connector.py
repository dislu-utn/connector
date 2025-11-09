from typing import Literal, TypedDict
from src.shared.integrate_dto import IntegrateDTO
from src.shared.transformer import TransformedRequest
from src.to_adaptaria.adaptaria_provider import AdaptariaProvider
from src.to_dislu.dislu_provider import DisluProvider


class Connector():

    def __init__(self, origin: Literal["dislu", "adaptaria"]):
        self.origin = origin
        
        if origin == "adaptaria":
            self.provider = DisluProvider()
        elif origin == "dislu":
            self.provider = AdaptariaProvider()
        else:
            raise Exception("Invalid origin")
    
    def integrate(self, message: IntegrateDTO): 
        self.provider.validate_request(message.institution_id)
        self.provider.initialize(message)
        return self.provider.transform()

    def initial_sync(self, message: IntegrateDTO): 

        self.provider.initialize(message)
        return self.provider.initial_sync()
