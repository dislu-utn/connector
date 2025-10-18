from main import IntegrateDTO
from src.providers.adaptaria.adaptaria_provider import AdaptariaProvider
from src.providers.dislu.dislu_provider import DisluProvider


class Connector():

    def __init__(self, origin: str):
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
        """

        self.provider.transform(message)
        
        return True
