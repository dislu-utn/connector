from typing import Any, Dict

import requests
from src.shared.transformer import TransformedRequest
from src.dislu.utils.endpoints import DisluEndpoints, InstitutionEndpoints
from src.shared.provider import Provider
from src.dislu.transformer.institutions_transformers import DisluInstitutionsTransformer


class DisluProvider(Provider):
    
    def transform(self): 
        if DisluEndpoints.INSTITUTIONS.value in self.endpoint:
            return DisluInstitutionsTransformer().run(self.endpoint, self.method, self.payload)
        if DisluEndpoints.COURSES.value in self.endpoint:
            pass
        if DisluEndpoints.ROADMAPS.value in self.endpoint:
            pass
        if DisluEndpoints.STUDY_MATERIALS.value in self.endpoint:
            pass
        if DisluEndpoints.USER_X_COURSE.value in self.endpoint:
            pass
        if DisluEndpoints.USERS.value in self.endpoint:
            pass
        return None

    def provide(self, request: TransformedRequest) -> requests.Response | None:
        response = super().provide(request)
        
        if self.endpoint.endswith("/create"):
            self.update_external_ref(response.json()["_id"])
        
        return response
        


    def update_external_ref(self, external_id: str):
        if not self.payload.get("id"):
            return None 
        
        update_endpoint = self.endpoint.replace("/create", "/update") 
        return requests.post(update_endpoint, json={
          "id": self.payload["id"],
          "external_reference": external_id
        })
