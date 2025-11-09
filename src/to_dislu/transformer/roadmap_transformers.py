from ast import List
import requests
from src.to_dislu.utils.endpoints import CourseEndpoints, DisluEndpoints, InstitutionEndpoints, RoadmapEndpoints
from src.shared.transformer import TransformedRequest, Transformer
from src.to_adaptaria.utils.endpoints import AdaptariaEndpoints, AdaptariaSectionEndpoints
from src.to_dislu.transformer.users_transformers import DisluUsersTransformer
from src.shared.logger import connector_logger, APIRequestError, ValidationError

class DisluRoadmapTransformer(Transformer):

    def run(self, entity:str, entity_id: str, method:str):
        try:
            connector_logger.info(f"Starting DisluRoadmapTransformer - Entity: {entity}, ID: {entity_id}, Method: {method}")
            
            if "create" in method:
                result = self.create(entity, entity_id)
                connector_logger.info(f"Successfully created roadmap in Dislu - Entity: {entity}, ID: {entity_id}")
                return result
            if "update" in method:
                result = self.update(entity, entity_id)
                connector_logger.info(f"Successfully updated roadmap in Dislu - Entity: {entity}, ID: {entity_id}")
                return result

            connector_logger.warning(f"No handler found for method: {method}")
            return None
            
        except Exception as e:
            connector_logger.error(f"Error in DisluRoadmapTransformer - Entity: {entity}, ID: {entity_id}, Method: {method} | Error: {str(e)}", exc_info=True)
            raise

    def create(self, entity: str, entity_id:str):
        try:
            connector_logger.info(f"Creating roadmap in Dislu from Adaptaria section - ID: {entity_id}")
            
            #entity_id = courseId/sectionId
            if "/" not in entity_id:
                raise ValidationError("Invalid entity_id format, expected 'courseId/sectionId'", entity=entity, entity_id=entity_id)
            
            adaptaria_course_id, adaptaria_section_id = entity_id.split("/")
            connector_logger.debug(f"Course: {adaptaria_course_id}, Section: {adaptaria_section_id}")
            
            adaptaria_section = self.adaptaria_api.request(AdaptariaSectionEndpoints.GET, "get", {}, {"courseId":adaptaria_course_id, "sectionId": adaptaria_section_id})
            print(adaptaria_section)
            if not adaptaria_section:
                raise ValidationError("Section not found in Adaptaria", entity=entity, entity_id=adaptaria_section_id)
            
            dislu_course = self.dislu_api.request(CourseEndpoints.GET_EXTERNAL, "get", {}, {"id":adaptaria_course_id})
            if not dislu_course:
                raise ValidationError("Course not found in Dislu with external reference", entity=entity, entity_id=adaptaria_course_id)

            # Validar campos requeridos
            if not adaptaria_section.get("name"):
                raise ValidationError("Section name is required", entity=entity, entity_id=adaptaria_section_id)

            payload = {
                "name": adaptaria_section.get("name"),
                "description": adaptaria_section.get("description") or "",
                "external_reference": adaptaria_section.get("id"),
                "course_id": dislu_course.get("id")
            }

            connector_logger.info(f"Creating roadmap in Dislu: {payload['name']}")
            response = self.dislu_api.request(
                RoadmapEndpoints.CREATE,
                "post",
                payload
            )
            
            if not response:
                raise APIRequestError("Failed to create roadmap in Dislu", entity=entity, entity_id=entity_id)
            
            connector_logger.info(f"Roadmap created successfully in Dislu")
            return response
            
        except (ValidationError, APIRequestError) as e:
            connector_logger.error(f"Validation/API error creating roadmap: {str(e)}")
            raise
        except Exception as e:
            connector_logger.error(f"Unexpected error creating roadmap in Dislu - ID: {entity_id} | Error: {str(e)}", exc_info=True)
            raise APIRequestError(f"Failed to create roadmap: {str(e)}", entity=entity, entity_id=entity_id)

    def update(self, entity: str, entity_id:str):
        try:
            connector_logger.info(f"Updating roadmap in Dislu from Adaptaria section - ID: {entity_id}")
            
            if "/" not in entity_id:
                raise ValidationError("Invalid entity_id format, expected 'courseId/sectionId'", entity=entity, entity_id=entity_id)
            
            adaptaria_course_id, adaptaria_section_id = entity_id.split("/")
            connector_logger.debug(f"Course: {adaptaria_course_id}, Section: {adaptaria_section_id}")
            
            adaptaria_section = self.adaptaria_api.request(AdaptariaSectionEndpoints.GET, "get", {}, {"courseId":adaptaria_course_id, "sectionId": adaptaria_section_id})
            if not adaptaria_section:
                raise ValidationError("Section not found in Adaptaria", entity=entity, entity_id=adaptaria_section_id)
                
            dislu_roadmap = self.dislu_api.request(RoadmapEndpoints.GET_EXTERNAL, "get", {}, {"id":adaptaria_section_id})
            if not dislu_roadmap:
                raise ValidationError("Roadmap not found in Dislu with external reference", entity=entity, entity_id=adaptaria_section_id)

            connector_logger.debug(f"Comparing roadmaps - Adaptaria: {adaptaria_section.get('name')}, Dislu: {dislu_roadmap.get('name')}")

            payload = {}

            if adaptaria_section.get("name") != dislu_roadmap.get("name"):
                payload["name"] = adaptaria_section.get("name")
                connector_logger.debug(f"Name needs update: {adaptaria_section.get('name')}")
            
            if adaptaria_section.get("description") != dislu_roadmap.get("description"):
                payload["description"] = adaptaria_section.get("description") or ""
                connector_logger.debug(f"Description needs update")

            if not payload:
                connector_logger.info(f"No roadmap fields need updating for {entity_id}")
                return None

            payload["id"] = dislu_roadmap.get("id")

            connector_logger.info(f"Updating roadmap fields in Dislu: {list(payload.keys())}")
            response = self.dislu_api.request(RoadmapEndpoints.UPDATE, "post", payload)
            connector_logger.info(f"Roadmap updated successfully in Dislu")
            return response
            
        except (ValidationError, APIRequestError) as e:
            connector_logger.error(f"Validation/API error updating roadmap: {str(e)}")
            raise
        except Exception as e:
            connector_logger.error(f"Unexpected error updating roadmap in Dislu - ID: {entity_id} | Error: {str(e)}", exc_info=True)
            raise APIRequestError(f"Failed to update roadmap: {str(e)}", entity=entity, entity_id=entity_id)
        

