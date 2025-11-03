import requests
from src.to_dislu.utils.endpoints import CourseEndpoints, DisluEndpoints, InstitutionEndpoints, RoadmapEndpoints
from src.shared.transformer import TransformedRequest, Transformer
from src.to_adaptaria.utils.endpoints import AdaptariaCourseEndpoints, AdaptariaEndpoints, AdaptariaSectionEndpoints

class AdaptariaSubjectTransformer(Transformer):

    def run(self, entity:str, entity_id: str, method:str):

        if "create" in method:
            return self.create(entity, entity_id)
        if "update" in method:
            return self.update(entity, entity_id)
        
        return None 

    def create(self, entity: str, entity_id:str):
        dislu_roadmap = self.dislu_api.request(RoadmapEndpoints.GET, "get", None, {"id": entity_id})
        return self.adaptaria_api.request(
            AdaptariaSectionEndpoints.CREATE,
            "post",
            {
                "name": dislu_roadmap.get("name"),
                "description": dislu_roadmap.get("description"),
                "visible": True
            },
            {
                "courseId": dislu_roadmap.get("course_id")
            }
        )

    def update(self, entity: str, entity_id:str):
        dislu_roadmap = self.dislu_api.request(RoadmapEndpoints.GET, "get", None, {"id": entity_id})
        adaptaria_section = self.dislu_api.request(AdaptariaSectionEndpoints.GET, "get", None, {"id": dislu_roadmap.get("external_reference")})

        payload = {}

        if adaptaria_section.get("title") != dislu_roadmap.get("name"):
            payload["title"] = dislu_roadmap.get("name")

        if adaptaria_section.get("description") != dislu_roadmap.get("description"):
            payload["description"] = dislu_roadmap.get("description")

        if not payload:
            return

        return self.adaptaria_api.request(
            AdaptariaSectionEndpoints.UPDATE,
            "post",
            {
                "name": dislu_roadmap.get("name"),
                "description": dislu_roadmap.get("description"),
                "visible": True
            },
            {
                "courseId": dislu_roadmap.get("course_id"),
                "sectionId": dislu_roadmap.get("external_reference")
            }
        )

