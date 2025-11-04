import io
import requests
from src.to_dislu.utils.endpoints import CourseEndpoints, DisluEndpoints, InstitutionEndpoints, RoadmapEndpoints, StudyMaterialEndpoints
from src.shared.transformer import TransformedRequest, Transformer
from src.to_adaptaria.utils.endpoints import AdaptariaContentEndpoints, AdaptariaCourseEndpoints, AdaptariaEndpoints

class AdaptariaContentsTransformer(Transformer):

    def run(self, entity:str, entity_id: str, method:str):

        #El create del curso se maneja en users_transformers
        if "create" in method:
            return self.create(entity, entity_id)
        
        return None 



    def create(self, entity: str, entity_id:str):
        dislu_study_material = self.dislu_api.request(StudyMaterialEndpoints.GET, "get", {"id":entity_id})

        dislu_roadmap = self.dislu_api.request(RoadmapEndpoints.GET, "get", {"id":dislu_study_material.get("roadmap_id")})
        if not dislu_roadmap or not dislu_roadmap.get("external_reference"):
            return None
        
        link = dislu_study_material.get("link")
        if not link:
            raise ValueError("link no encontrado en dislu_study_material")
        
        # Descargar el archivo desde S3 en memoria
        file_response = requests.get(link)
        file_response.raise_for_status()
        
        # Crear un objeto tipo archivo en memoria
        file_content = io.BytesIO(file_response.content)
        
        # Archivo a subir (en memoria)
        files = {
            "file": (dislu_study_material.get("name", "document"), file_content, file_response.headers.get("content-type", "application/octet-stream"))
        }

        return self.adaptaria_api.request(
            AdaptariaContentEndpoints.CREATE, 
            "post", 
            {
                "title": dislu_study_material.get("name", "document"),
                "publicationType":"AUTOMATIC",
                "visible": False
            }, 
            {
                "sectionId": dislu_roadmap.get("external_reference")
            },
            files
        )
        

