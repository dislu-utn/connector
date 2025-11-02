import requests
from src.to_dislu.utils.endpoints import CourseEndpoints, DisluEndpoints, InstitutionEndpoints
from src.shared.transformer import TransformedRequest, Transformer
from src.to_adaptaria.utils.endpoints import AdaptariaEndpoints

class AdaptariaCoursesTransformer(Transformer):

    def run(self, entity:str, entity_id: str, method:str):

        if "create" in method:
            return self.create(entity, entity_id)
        if "update" in method:
            return self.update(entity, entity_id)
        
        return None 

    def create(self, entity: str, entity_id:str):
        dislu_course = self.dislu_api.request(CourseEndpoints.GET_EXTERNAL, "get", {"id": entity_id})

        payload = {
            "title": dislu_course.get("name"),
            "description": dislu_course.get("description"),
            "matriculationCode": dislu_course.get("matriculation_key"),
        }

        response = self.adaptaria_api.request(AdaptariaEndpoints.COURSES, "post", payload)
        
        self.dislu_api.update_external_reference(
            CourseEndpoints.UPDATE, 
            dislu_course.get("id"), 
            response.get("id")
            )

        return response

    def update(self, entity: str, entity_id:str):
        adaptaria_course = self.adaptaria_api.request(AdaptariaEndpoints.COURSES, "get", {"id":entity_id})
        dislu_course = self.dislu_api.request(CourseEndpoints.GET_EXTERNAL, "get", {"id": entity_id})

        payload = {}

        if adaptaria_course.get("title") != dislu_course.get("name"):
            payload["title"] = dislu_course.get("name")

        if adaptaria_course.get("description") != dislu_course.get("description"):
            payload["description"] = dislu_course.get("description")

        if adaptaria_course.get("matriculationCode") != dislu_course.get("matriculation_key"):
            payload["matriculationCode"] = dislu_course.get("matriculation_key")

        if not payload:
            return

        return self.adaptaria_api.request(AdaptariaEndpoints.COURSES, "patch", payload)
        

