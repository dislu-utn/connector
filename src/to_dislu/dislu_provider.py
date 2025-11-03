from typing import Any, Dict

import requests
from src.to_dislu.transformer.courses_transformers import DisluCoursesTransformer
from src.shared.transformer import TransformedRequest
from src.to_dislu.utils.endpoints import DisluEndpoints, InstitutionEndpoints
from src.shared.provider import Provider
from src.to_dislu.transformer.users_transformers import DisluUsersTransformer
from src.to_dislu.transformer.users_x_courses_transformers import DisluUsersXCoursesTransformer


class DisluProvider(Provider):
    
    def transform(self): 
        if self.entity == "institution":
            #return DisluInstitutionsTransformer().run(self.entity_id, self.endpoint, self.method, self.payload)
            pass
        if self.entity == "course":
            return DisluCoursesTransformer(self.institution_id).run(self.entity, self.entity_id, self.method)
        if self.entity == ["user","student", "teacher", "director"]:
            return DisluUsersTransformer(self.institution_id).run(self.entity, self.entity_id, self.method)
        return None
