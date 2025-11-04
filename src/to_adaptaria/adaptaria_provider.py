from src.shared.provider import Provider
from src.to_adaptaria.transformer.courses_transformer import AdaptariaCoursesTransformer
from src.to_adaptaria.transformer.users_transformers import AdaptariaUsersTransformer
from src.to_adaptaria.transformer.contents_transformer import AdaptariaContentsTransformer
from src.to_adaptaria.transformer.subject_transformers import AdaptariaSubjectTransformer


class AdaptariaProvider(Provider):
    
    def transform(self): 
        if self.entity == "course":
            return AdaptariaCoursesTransformer(self.institution_id).run(self.entity, self.entity_id, self.method)
        if self.entity == "roadmap":
            return AdaptariaSubjectTransformer(self.institution_id).run(self.entity, self.entity_id, self.method)
        if self.entity == "study_material":
            return AdaptariaContentsTransformer(self.institution_id).run(self.entity, self.entity_id, self.method)
        if self.entity in ["user", "student", "professor", "admin"]:
            return AdaptariaUsersTransformer(self.institution_id).run(self.entity, self.entity_id, self.method)
            
        return None




