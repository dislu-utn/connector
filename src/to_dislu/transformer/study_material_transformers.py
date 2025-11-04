from ast import List
import io
import requests
from src.to_dislu.utils.endpoints import CourseEndpoints, DisluEndpoints, InstitutionEndpoints, RoadmapEndpoints, StudyMaterialEndpoints
from src.shared.transformer import TransformedRequest, Transformer
from src.to_adaptaria.utils.endpoints import AdaptariaContentEndpoints, AdaptariaEndpoints
from to_dislu.transformer.users_transformers import DisluUsersTransformer

class DisluStudyMaterialTransformer(Transformer):

    def run(self, entity:str, entity_id: str, method:str):

        if "create" in method:
            return self.create(entity, entity_id)
        if "update" in method:
            return self.update(entity, entity_id)

        return None 

    def create(self, entity: str, entity_id:str):
        adaptaria_content = self.adaptaria_api.request(AdaptariaContentEndpoints.GET, "get", None, {"id":entity_id})
        dislu_roadmap = self.dislu_api.request(RoadmapEndpoints.GET_EXTERNAL, "get", None, {"id": adaptaria_content.get("sectionId")})

        if not dislu_roadmap:
            return None

        # Obtener el archivo desde S3 usando la URL presignada
        presigned_url = adaptaria_content.get("presignedUrl")
        if not presigned_url:
            raise ValueError("presignedUrl no encontrado en adaptaria_content")
        
        # Descargar el archivo desde S3 en memoria
        file_response = requests.get(presigned_url)
        file_response.raise_for_status()
        
        # Obtener el nombre del archivo desde la key o usar un nombre por defecto
        file_key = adaptaria_content.get("key", "document.pdf")
        file_name = file_key.split("/")[-1] if "/" in file_key else file_key
        
        # Crear un objeto tipo archivo en memoria
        file_content = io.BytesIO(file_response.content)
        
        # Archivo a subir (en memoria)
        files = {
            "file": (file_name, file_content, file_response.headers.get("content-type", "application/octet-stream"))
        }

        return self.dislu_api.request(
            StudyMaterialEndpoints.CREATE,
            "post",
            {
                "roadmap_id": dislu_roadmap.get("id")
            },
            None,
            files
        )

    def update(self, entity: str, entity_id:str):
        adaptaria_course = self.adaptaria_api.request(AdaptariaEndpoints.COURSES, "get", None,{"id":entity_id})
        dislu_course = self.dislu_api.request(CourseEndpoints.GET_EXTERNAL, "get", None,{"id": entity_id})

        payload = {}

        if adaptaria_course.get("title") != dislu_course.get("name"):
            payload["name"] = dislu_course.get("title")

        if adaptaria_course.get("description") != dislu_course.get("description"):
            payload["description"] = dislu_course.get("description")

        """ Por ahora no tenemos imagenes en los cursos de Dislu
        if adaptaria_course.get("image") != dislu_course.get("image"):
            payload["image"] = dislu_course.get("image")
        """

        if not payload:
            return

        payload["id"] = dislu_course.get("id")
        return self.dislu_api.request(CourseEndpoints.UPDATE, "post", payload)
        

