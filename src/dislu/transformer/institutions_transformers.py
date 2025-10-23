from src.adaptaria.utils.endpoints import InstituteEndpoints
from src.dislu.utils.endpoints import InstitutionEndpoints
from src.shared.transformer import TransformedRequest, Transformer
from src.adaptaria.transformer.models import AdaptariaCreateInstitutePayload
from src.dislu.transformer.models import DisluCreateInstitutionPayload

class DisluInstitutionsTransformer(Transformer):

    def run(self, endpoint:str, method:str, body: DisluCreateInstitutionPayload):
        """
        - Esto debería devolver el endpoint para pegarle a adaptaria junto al payload
        """
        if InstitutionEndpoints.CREATE.value in endpoint:
            return self.institution_create(endpoint, body)
        
        return None 

    def institution_create(self, endpoint: str, payload: DisluCreateInstitutionPayload) -> TransformedRequest:
        """
        Transform dislu payload into adaptaria payload
        """
        adaptaria_body: AdaptariaCreateInstitutePayload = {
            "name": payload["name"],
            "address": "",
            "phone": ""
        }
        
        return TransformedRequest(
            url=InstituteEndpoints.CREATE.value,
            method="post",
            payload=adaptaria_body
        )
        

