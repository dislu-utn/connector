import requests
from src.to_dislu.utils.endpoints import CourseEndpoints, DisluEndpoints, InstitutionEndpoints
from src.shared.transformer import TransformedRequest, Transformer
from src.to_adaptaria.utils.endpoints import AdaptariaCourseEndpoints, AdaptariaEndpoints

class AdaptariaCoursesTransformer(Transformer):

    def run(self, entity:str, entity_id: str, method:str):

        #El create del curso se maneja en users_transformers
        if "update" in method:
            return self.create(entity, entity_id)
        
        return None 



    def update(self, entity: str, entity_id:str):
        adaptaria_course = self.adaptaria_api.request(AdaptariaEndpoints.COURSES, "get", {"id":entity_id})
        dislu_course = self.dislu_api.request(CourseEndpoints.GET_EXTERNAL, "get", {"id": entity_id})

        payload = {}

        if adaptaria_course.get("title") != dislu_course.get("name"):
            payload["title"] = dislu_course.get("name")

        if adaptaria_course.get("description") != dislu_course.get("description"):
            payload["description"] = dislu_course.get("description")

        """ Por ahora no tenemos imagenes en los cursos de Dislu
        if adaptaria_course.get("image") != dislu_course.get("image"):
            payload["image"] = dislu_course.get("image")
        """

        if not payload:
            return

        payload["id"] = entity_id

        return self.adaptaria_api.request(AdaptariaCourseEndpoints.UPDATE, "patch", payload)
        

