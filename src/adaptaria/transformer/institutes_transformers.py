from typing import Dict, Any, Literal

from src.adaptaria.transformer.models import AdaptariaCreateInstitutePayload
from src.dislu.transformer.models import DisluCreateInstitutionPayload

from src.adaptaria.utils.endpoints import InstituteEndpoints
from src.dislu.utils.endpoints import InstitutionEndpoints
from src.shared.transformer import TransformedRequest, Transformer

class AdaptariaInstitutesTransformer(Transformer):

    def run(self, endpoint:str, method:Literal["post", "patch"], body: AdaptariaCreateInstitutePayload):
        if method == "post":
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
        
