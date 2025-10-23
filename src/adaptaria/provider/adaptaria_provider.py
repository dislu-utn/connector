from typing import Any, Dict

from src.adaptaria.transformer.institutes_transformers import AdaptariaInstitutesTransformer
from src.adaptaria.utils.endpoints import AdaptariaEndpoints
from src.shared.provider import Provider


class AdaptariaProvider(Provider):
    
    def transform(self): 
        if AdaptariaEndpoints.INSTITUTES.value in self.endpoint:
            return AdaptariaInstitutesTransformer().run(self.endpoint, self.method, self.payload)

        #if AdaptariaEndpoints.COURSES.value in endpoint:
        #    pass

            
        return None




