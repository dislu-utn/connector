from ast import List
import requests
from src.to_dislu.utils.endpoints import CourseEndpoints, DisluEndpoints, InstitutionEndpoints, RoadmapEndpoints
from src.shared.transformer import TransformedRequest, Transformer
from src.to_adaptaria.utils.endpoints import AdaptariaEndpoints, AdaptariaSectionEndpoints
from src.to_dislu.transformer.users_transformers import DisluUsersTransformer

class DisluRoadmapTransformer(Transformer):

    def run(self, entity:str, entity_id: str, method:str):

        if "create" in method:
            return self.create(entity, entity_id)
        if "update" in method:
            return self.update(entity, entity_id)

        return None 

    def create(self, entity: str, entity_id:str):
        #entity_id = courseId/sectionId
        adaptaria_course_id, adaptaria_section_id = entity.split("/")
        adaptaria_section = self.adaptaria_api.request(AdaptariaSectionEndpoints.GET, "get", None, {"courseId":adaptaria_course_id, "sectionId": adaptaria_section_id})
        dislu_course = self.dislu_api.request(CourseEndpoints.GET_EXTERNAL, "get", None, {"id":adaptaria_course_id})

        return self.dislu_api.request(
            RoadmapEndpoints.CREATE,
            "post",
            {
                "name": adaptaria_section.get("name"),
                "description": adaptaria_section.get("description"),
                "external_reference": adaptaria_section.get("id"),
                "course_id": dislu_course.get("id")
            }
        )

    def update(self, entity: str, entity_id:str):
        adaptaria_course_id, adaptaria_section_id = entity.split("/")
        adaptaria_section = self.adaptaria_api.request(AdaptariaSectionEndpoints.GET, "get", None, {"courseId":adaptaria_course_id, "sectionId": adaptaria_section_id})
        dislu_roadmap = self.dislu_api.request(RoadmapEndpoints.GET_EXTERNAL, "get", None, {"id":adaptaria_section_id})

        payload = {}

        if adaptaria_section.get("name") != dislu_roadmap.get("name"):
            payload["name"] = adaptaria_section.get("name")
        
        if adaptaria_section.get("description") != dislu_roadmap.get("description"):
            payload["description"] = adaptaria_section.get("description")

        if not payload:
            return None

        payload["id"] = dislu_roadmap.get("id")

        return self.dislu_api.request(RoadmapEndpoints.UPDATE, "post", payload)
        

