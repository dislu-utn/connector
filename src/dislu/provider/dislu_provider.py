from typing import Any, Dict
from src.dislu.utils.endpoints import DisluEndpoints
from src.shared.provider import Provider
from src.dislu.transformer.institutions_transformers import DisluInstitutionsTransformer


class DisluProvider(Provider):
    
    def transform(self, endpoint:str, method:str, payload: Dict[str, Any]): 
        if DisluEndpoints.INSTITUTIONS.value in endpoint:
            return DisluInstitutionsTransformer().run(endpoint, method, payload)
        if DisluEndpoints.COURSES.value in endpoint:
            pass
        if DisluEndpoints.ROADMAPS.value in endpoint:
            pass
        if DisluEndpoints.STUDY_MATERIALS.value in endpoint:
            pass
        if DisluEndpoints.USER_X_COURSE.value in endpoint:
            pass
        if DisluEndpoints.USERS.value in endpoint:
            pass
        return None
