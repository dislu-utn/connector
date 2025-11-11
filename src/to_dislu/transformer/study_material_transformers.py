from ast import List
import io
import requests
from src.to_dislu.utils.endpoints import CourseEndpoints, DisluEndpoints, InstitutionEndpoints, RoadmapEndpoints, StudyMaterialEndpoints
from src.shared.transformer import TransformedRequest, Transformer
from src.to_adaptaria.utils.endpoints import AdaptariaContentEndpoints, AdaptariaEndpoints
from src.to_dislu.transformer.users_transformers import DisluUsersTransformer
from src.shared.logger import connector_logger, APIRequestError, ValidationError

class DisluStudyMaterialTransformer(Transformer):

    def run(self, entity:str, entity_id: str, method:str):
        try:
            connector_logger.info(f"Starting DisluStudyMaterialTransformer - Entity: {entity}, ID: {entity_id}, Method: {method}")
            
            if "create" in method:
                result = self.create(entity, entity_id)
                connector_logger.info(f"Successfully created study material in Dislu - Entity: {entity}, ID: {entity_id}")
                return result

            connector_logger.warning(f"No handler found for method: {method}")
            return None
            
        except Exception as e:
            connector_logger.error(f"Error in DisluStudyMaterialTransformer - Entity: {entity}, ID: {entity_id}, Method: {method} | Error: {str(e)}", exc_info=True)
            raise

    def create(self, entity: str, entity_id:str):
        try:
            connector_logger.info(f"Creating study material in Dislu from Adaptaria content - ID: {entity_id}")
            
            adaptaria_content = self.adaptaria_api.request(AdaptariaContentEndpoints.GET, "get", {}, {"id":entity_id})
            if not adaptaria_content:
                raise ValidationError("Content not found in Adaptaria", entity=entity, entity_id=entity_id)
            
            connector_logger.debug(f"Retrieved Adaptaria content: {adaptaria_content.get('title')}")
            
            dislu_roadmap = self.dislu_api.request(RoadmapEndpoints.GET_EXTERNAL, "get", {}, {"id": adaptaria_content.get("sectionId")})

            if not dislu_roadmap:
                connector_logger.warning(f"Roadmap not found for content {entity_id}")
                return None

            # Obtener el archivo desde S3 usando la URL presignada
            presigned_url = adaptaria_content.get("presignedUrl")
            if not presigned_url:
                raise ValidationError("presignedUrl not found in adaptaria_content", entity=entity, entity_id=entity_id)
            
            connector_logger.info(f"Downloading file from S3: {presigned_url}")
            # Descargar el archivo desde S3 en memoria
            file_response = requests.get(presigned_url)
            file_response.raise_for_status()
            
            connector_logger.debug(f"File downloaded successfully - Content-Type: {file_response.headers.get('content-type')}, Size: {len(file_response.content)} bytes")
            
            # Obtener el nombre del archivo desde la key o usar un nombre por defecto
            file_key = adaptaria_content.get("key", "document.pdf")
            file_name = adaptaria_content.get("title") if adaptaria_content.get("title") else file_key.split("/")[-1] if "/" in file_key else file_key
            
            # Crear un objeto tipo archivo en memoria
            file_content = io.BytesIO(file_response.content)
            
            # Archivo a subir (en memoria)
            files = {
                "file": (file_name, file_content, file_response.headers.get("content-type", "application/octet-stream"))
            }

            connector_logger.info(f"Uploading study material to Dislu roadmap {dislu_roadmap.get('id')}")
            response = self.dislu_api.request(
                StudyMaterialEndpoints.CREATE,
                "post",
                {
                    "roadmap_id": dislu_roadmap.get("id")
                },
                None,
                files
            )
            
            if not response:
                raise APIRequestError("Failed to create study material in Dislu", entity=entity, entity_id=entity_id)
            
            connector_logger.info(f"Study material created successfully in Dislu")
            return response
            
        except (ValidationError, APIRequestError) as e:
            connector_logger.error(f"Validation/API error creating study material: {str(e)}")
            raise
        except requests.exceptions.RequestException as e:
            connector_logger.error(f"Error downloading file from S3: {str(e)}", exc_info=True)
            raise APIRequestError(f"Failed to download file: {str(e)}", entity=entity, entity_id=entity_id)
        except Exception as e:
            connector_logger.error(f"Unexpected error creating study material in Dislu - ID: {entity_id} | Error: {str(e)}", exc_info=True)
            raise APIRequestError(f"Failed to create study material: {str(e)}", entity=entity, entity_id=entity_id)
