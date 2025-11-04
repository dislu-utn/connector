from typing import Any, Dict

import requests
from src.to_dislu.transformer.courses_transformers import DisluCoursesTransformer
from src.shared.transformer import TransformedRequest
from src.to_dislu.utils.endpoints import DisluEndpoints, InstitutionEndpoints
from src.shared.provider import Provider
from src.to_dislu.transformer.users_transformers import DisluUsersTransformer
from to_dislu.transformer.roadmap_transformers import DisluRoadmapTransformer
from to_dislu.transformer.study_material_transformers import DisluStudyMaterialTransformer


class DisluProvider(Provider):
    
    def transform(self): 
        if self.entity == "institution":
            #return DisluInstitutionsTransformer().run(self.entity_id, self.endpoint, self.method, self.payload)
            pass
        if self.entity == "course":
            return DisluCoursesTransformer(self.institution_id).run(self.entity, self.entity_id, self.method)
        if self.entity == ["user","student", "teacher", "director"]:
            return DisluUsersTransformer(self.institution_id).run(self.entity, self.entity_id, self.method)
        if self.entity == "subject":
            return DisluRoadmapTransformer(self.institution_id).run(self.entity, self.entity_id, self.method)
        if self.entity == "content":
            return DisluStudyMaterialTransformer(self.institution_id).run(self.entity, self.entity_id, self.method)

        return None
