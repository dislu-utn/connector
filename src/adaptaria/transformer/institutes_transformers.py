from typing import Dict, Any
from src.dislu.transformer.models.intitution_models import AdaptariaCreateInstitutePayload, DisluCreateInstitutionPayload
from src.adaptaria.utils.endpoints import InstituteEndpoints
from src.dislu.utils.endpoints import InstitutionEndpoints
from src.shared.transformer import TransformedRequest, Transformer

class AdaptariaInstitutesTransformer(Transformer):

    def run(self, endpoint:str, method:str, body: AdaptariaCreateInstitutePayload):
        if InstituteEndpoints.CREATE.value in endpoint:
            return self.institutes_create(endpoint, body)
        
        return None 

    def institutes_create(self, endpoint: str, payload: AdaptariaCreateInstitutePayload) -> TransformedRequest:
        dislu_body: DisluCreateInstitutionPayload = {
            "name": payload["name"],
            "domain": ""
        }
        
        return TransformedRequest(
            url=InstitutionEndpoints.CREATE.value,
            method="post",
            payload=dislu_body
        )
        
