from typing import Any, Dict
from src.adaptaria.transformer.institutes_transformers import AdaptariaInstitutesTransformer
from src.adaptaria.utils.endpoints import AdaptariaEndpoints
from src.shared.provider import Provider


class AdaptariaProvider(Provider):
    
    def transform(self, endpoint:str, method:str, payload: Dict[str, Any]): 
        if AdaptariaEndpoints.INSTITUTES.value in endpoint:
            return AdaptariaInstitutesTransformer().run(endpoint, method, payload)

        #if AdaptariaEndpoints.COURSES.value in endpoint:
        #    pass

            
        return None
