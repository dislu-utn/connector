import requests
from src.to_dislu.utils.endpoints import CourseEndpoints, DisluEndpoints, InstitutionEndpoints, RoadmapEndpoints
from src.shared.transformer import TransformedRequest, Transformer
from src.to_adaptaria.utils.endpoints import AdaptariaCourseEndpoints, AdaptariaEndpoints, AdaptariaSectionEndpoints
from src.shared.logger import connector_logger, APIRequestError, ValidationError

class AdaptariaSubjectTransformer(Transformer):

    def run(self, entity:str, entity_id: str, method:str):
        try:
            connector_logger.info(f"Starting AdaptariaSubjectTransformer - Entity: {entity}, ID: {entity_id}, Method: {method}")
            
            if "create" in method:
                result = self.create(entity, entity_id)
                connector_logger.info(f"Successfully created section in Adaptaria - Entity: {entity}, ID: {entity_id}")
                return result
            if "update" in method:
                result = self.update(entity, entity_id)
                connector_logger.info(f"Successfully updated section in Adaptaria - Entity: {entity}, ID: {entity_id}")
                return result
            
            connector_logger.warning(f"No handler found for method: {method}")
            return None
            
        except Exception as e:
            connector_logger.error(f"Error in AdaptariaSubjectTransformer - Entity: {entity}, ID: {entity_id}, Method: {method} | Error: {str(e)}", exc_info=True)
            raise 

    def create(self, entity: str, entity_id:str):
        try:
            connector_logger.info(f"Creating section in Adaptaria from roadmap - ID: {entity_id}")
            
            dislu_roadmap = self.dislu_api.request(RoadmapEndpoints.GET, "get", {}, {"id": entity_id})
            print(dislu_roadmap)
            if not dislu_roadmap:
                raise ValidationError("Roadmap not found in Dislu", entity=entity, entity_id=entity_id)
            
            if dislu_roadmap.get("external_reference"):
                 raise ValidationError("Roadmap in Dislu already has an external reference", entity=entity, entity_id=entity_id)
            
            dislu_course = self.dislu_api.request(CourseEndpoints.GET, "get", {}, {"id": dislu_roadmap.get("course_id")})
            print(dislu_course)

            # Validar campos requeridos
            if not dislu_roadmap.get("name"):
                raise ValidationError("Roadmap name is required", entity=entity, entity_id=entity_id)
            if not dislu_course.get("external_reference"):
                raise ValidationError("Roadmap course external_reference is required", entity=entity, entity_id=entity_id)
            
            connector_logger.debug(f"Creating section: {dislu_roadmap.get('name')} for course {dislu_roadmap.get('course_id')}")
            
            response = self.adaptaria_api.request(
                AdaptariaSectionEndpoints.CREATE,
                "post",
                {
                    "name": dislu_roadmap.get("name"),
                    "description": dislu_roadmap.get("description") or "",
                    "visible": True,
                    "image": "https://picsum.photos/300/200"
                },
                {
                    "courseId": dislu_course.get("external_reference")
                }
            )
            
            if not response or not response.get("id"):
                raise APIRequestError("Failed to create section in Adaptaria - no ID returned", entity=entity, entity_id=entity_id)
            
            connector_logger.info(f"Section created successfully in Adaptaria - ID: {response.get('id')}")
            
            # Actualizar referencia externa en Dislu
            self.dislu_api.update_external_reference(
                RoadmapEndpoints.UPDATE,
                dislu_roadmap.get("id"),
                response.get("id")
            )
            
            connector_logger.info(f"External reference updated in Dislu for roadmap {entity_id}")
            return response
            
        except (ValidationError, APIRequestError) as e:
            connector_logger.error(f"Validation/API error creating section: {str(e)}")
            raise
        except Exception as e:
            connector_logger.error(f"Unexpected error creating section in Adaptaria - ID: {entity_id} | Error: {str(e)}", exc_info=True)
            raise APIRequestError(f"Failed to create section: {str(e)}", entity=entity, entity_id=entity_id)

    def update(self, entity: str, entity_id:str):
        try:
            connector_logger.info(f"Updating section in Adaptaria - Roadmap ID: {entity_id}")
            
            dislu_roadmap = self.dislu_api.request(RoadmapEndpoints.GET, "get", {}, {"id": entity_id})
            if not dislu_roadmap:
                raise ValidationError("Roadmap not found in Dislu", entity=entity, entity_id=entity_id)
            
            if not dislu_roadmap.get("external_reference"):
                raise ValidationError("Roadmap has no external reference", entity=entity, entity_id=entity_id)
                
            adaptaria_section = self.adaptaria_api.request(AdaptariaSectionEndpoints.GET, "get", {}, {"id": dislu_roadmap.get("external_reference")})
            if not adaptaria_section:
                raise ValidationError("Section not found in Adaptaria", entity=entity, entity_id=dislu_roadmap.get("external_reference"))

            connector_logger.debug(f"Comparing sections - Adaptaria: {adaptaria_section.get('name')}, Dislu: {dislu_roadmap.get('name')}")

            payload = {}

            if adaptaria_section.get("name") != dislu_roadmap.get("name"):
                payload["name"] = dislu_roadmap.get("name")
                connector_logger.debug(f"Name needs update: {dislu_roadmap.get('name')}")

            if adaptaria_section.get("description") != dislu_roadmap.get("description"):
                payload["description"] = dislu_roadmap.get("description")
                connector_logger.debug(f"Description needs update")

            if not payload:
                connector_logger.info(f"No section fields need updating for {entity_id}")
                return

            connector_logger.info(f"Updating section fields in Adaptaria: {list(payload.keys())}")
            response = self.adaptaria_api.request(
                AdaptariaSectionEndpoints.UPDATE,
                "post",
                {
                    "name": dislu_roadmap.get("name"),
                    "description": dislu_roadmap.get("description") or "",
                    "visible": True
                },
                {
                    "courseId": adaptaria_section.get("courseId"),
                    "sectionId": dislu_roadmap.get("external_reference")
                }
            )
            connector_logger.info(f"Section updated successfully in Adaptaria")
            return response
            
        except (ValidationError, APIRequestError) as e:
            connector_logger.error(f"Validation/API error updating section: {str(e)}")
            raise
        except Exception as e:
            connector_logger.error(f"Unexpected error updating section in Adaptaria - ID: {entity_id} | Error: {str(e)}", exc_info=True)
            raise APIRequestError(f"Failed to update section: {str(e)}", entity=entity, entity_id=entity_id)

