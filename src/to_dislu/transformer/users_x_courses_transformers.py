import requests
from src.to_dislu.utils.endpoints import CourseEndpoints, DisluEndpoints, InstitutionEndpoints, UsersXCourseEndpoints
from src.shared.transformer import TransformedRequest, Transformer
from src.to_adaptaria.utils.endpoints import AdaptariaEndpoints

class DisluUsersXCoursesTransformer(Transformer):

    def run(self, entity:str, entity_id: str, method:str):

        if "create" in method:
            return self.create(entity, entity_id)
        if "update" in method:
            return self.update(entity, entity_id)
        
        return None 

