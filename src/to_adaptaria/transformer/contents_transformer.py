import io
import requests
from src.to_dislu.utils.endpoints import CourseEndpoints, DisluEndpoints, InstitutionEndpoints, RoadmapEndpoints, StudyMaterialEndpoints
from src.shared.transformer import TransformedRequest, Transformer
from src.to_adaptaria.utils.endpoints import AdaptariaContentEndpoints, AdaptariaCourseEndpoints, AdaptariaEndpoints
from src.shared.logger import connector_logger, APIRequestError, ValidationError

class AdaptariaContentsTransformer(Transformer):

    def run(self, entity:str, entity_id: str, method:str):
        try:
            connector_logger.info(f"Starting AdaptariaContentsTransformer - Entity: {entity}, ID: {entity_id}, Method: {method}")
            
            #El create del curso se maneja en users_transformers
            if "create" in method:
                result = self.create(entity, entity_id)
                connector_logger.info(f"Successfully created content in Adaptaria - Entity: {entity}, ID: {entity_id}")
                return result
            
            connector_logger.warning(f"No handler found for method: {method}")
            return None
            
        except Exception as e:
            connector_logger.error(f"Error in AdaptariaContentsTransformer - Entity: {entity}, ID: {entity_id}, Method: {method} | Error: {str(e)}", exc_info=True)
            raise 



    def create(self, entity: str, entity_id:str):
        try:
            connector_logger.info(f"Creating content in Adaptaria from study material - ID: {entity_id}")
            
            dislu_study_material = self.dislu_api.request(StudyMaterialEndpoints.GET, "get", {"id":entity_id})
            if not dislu_study_material:
                raise ValidationError("Study material not found in Dislu", entity=entity, entity_id=entity_id)
            
            connector_logger.debug(f"Study material: {dislu_study_material.get('name')}")

            dislu_roadmap = self.dislu_api.request(RoadmapEndpoints.GET, "get", {"id":dislu_study_material.get("roadmap_id")})
            if not dislu_roadmap:
                connector_logger.warning(f"Roadmap not found for study material {entity_id}")
                return None
                
            if not dislu_roadmap.get("external_reference"):
                connector_logger.warning(f"Roadmap {dislu_roadmap.get('id')} has no external reference in Adaptaria")
                return None
            
            link = dislu_study_material.get("link")
            if not link:
                raise ValidationError("Study material has no link", entity=entity, entity_id=entity_id)
            
            connector_logger.info(f"Downloading file from S3: {link}")
            # Descargar el archivo desde S3 en memoria
            file_response = requests.get(link)
            file_response.raise_for_status()
            
            connector_logger.debug(f"File downloaded successfully - Content-Type: {file_response.headers.get('content-type')}, Size: {len(file_response.content)} bytes")
            
            # Crear un objeto tipo archivo en memoria
            file_content = io.BytesIO(file_response.content)
            
            # Archivo a subir (en memoria)
            files = {
                "file": (dislu_study_material.get("name", "document"), file_content, file_response.headers.get("content-type", "application/octet-stream"))
            }

            connector_logger.info(f"Uploading content to Adaptaria section {dislu_roadmap.get('external_reference')}")
            response = self.adaptaria_api.request(
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
            
            if not response:
                raise APIRequestError("Failed to create content in Adaptaria", entity=entity, entity_id=entity_id)
            
            connector_logger.info(f"Content created successfully in Adaptaria")
            return response
            
        except (ValidationError, APIRequestError) as e:
            connector_logger.error(f"Validation/API error creating content: {str(e)}")
            raise
        except requests.exceptions.RequestException as e:
            connector_logger.error(f"Error downloading file from S3: {str(e)}", exc_info=True)
            raise APIRequestError(f"Failed to download file: {str(e)}", entity=entity, entity_id=entity_id)
        except Exception as e:
            connector_logger.error(f"Unexpected error creating content in Adaptaria - ID: {entity_id} | Error: {str(e)}", exc_info=True)
            raise APIRequestError(f"Failed to create content: {str(e)}", entity=entity, entity_id=entity_id)
        

