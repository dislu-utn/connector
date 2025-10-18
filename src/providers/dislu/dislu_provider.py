from src.providers.provider import Provider


class DisluProvider(Provider):
    
    def transform(self, endpoint:str, method:str, consumer:str, body: dict): 
        """
        if endpoint, consumer : llamar tal
        if endpoint2, consumer2 : llamar tal2
        ...

        """
        
        pass
    
