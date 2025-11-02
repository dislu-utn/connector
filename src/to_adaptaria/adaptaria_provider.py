from typing import Any, Dict

from src.to_adaptaria.utils.endpoints import AdaptariaEndpoints
from src.shared.provider import Provider
from src.to_adaptaria.transformer.courses_transformer import AdaptariaCoursesTransformer
from src.to_adaptaria.transformer.users_transformers import AdaptariaUsersTransformer


class AdaptariaProvider(Provider):
    
    def transform(self): 
        if self.entity == "course":
            AdaptariaCoursesTransformer(self.institution_id).run(self.entity, self.entity_id, self.method)
        if self.entity == "roadmap":
            pass
        if self.entity == "study_material":
            pass
        if self.entity == "user_x_course":
            pass
        if self.entity == ["user", "student", "professor", "admin"]:
            AdaptariaUsersTransformer(self.institution_id).run(self.entity, self.entity_id, self.method)
            pass
        #if AdaptariaEndpoints.COURSES.value in endpoint:
        #    pass

            
        return None




