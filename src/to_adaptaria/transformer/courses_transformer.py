import requests
from src.to_dislu.utils.endpoints import CourseEndpoints, DisluEndpoints, InstitutionEndpoints
from src.shared.transformer import TransformedRequest, Transformer
from src.to_adaptaria.utils.endpoints import AdaptariaCourseEndpoints, AdaptariaEndpoints
from src.shared.logger import connector_logger, APIRequestError, ValidationError

class AdaptariaCoursesTransformer(Transformer):

    def run(self, entity:str, entity_id: str, method:str):
        try:
            connector_logger.info(f"Starting AdaptariaCoursesTransformer - Entity: {entity}, ID: {entity_id}, Method: {method}")
            
            #El create del curso se maneja en users_transformers
            if "update" in method:
                result = self.update(entity, entity_id)
                connector_logger.info(f"Successfully updated course in Adaptaria - Entity: {entity}, ID: {entity_id}")
                return result
            
            connector_logger.warning(f"No handler found for method: {method}")
            return None
            
        except Exception as e:
            connector_logger.error(f"Error in AdaptariaCoursesTransformer - Entity: {entity}, ID: {entity_id}, Method: {method} | Error: {str(e)}", exc_info=True)
            raise



    def update(self, entity: str, entity_id:str):
        try:
            connector_logger.info(f"Updating course in Adaptaria - ID: {entity_id}")
            
            # Obtener curso de Adaptaria
            adaptaria_course = self.adaptaria_api.request(AdaptariaEndpoints.COURSES, "get", {"id":entity_id})
            if not adaptaria_course:
                raise ValidationError("Course not found in Adaptaria", entity=entity, entity_id=entity_id)
            
            # Obtener curso de Dislu
            dislu_course = self.dislu_api.request(CourseEndpoints.GET_EXTERNAL, "get", {"id": entity_id})
            if not dislu_course:
                raise ValidationError("Course not found in Dislu with external reference", entity=entity, entity_id=entity_id)
            
            connector_logger.debug(f"Comparing courses - Adaptaria: {adaptaria_course.get('title')}, Dislu: {dislu_course.get('name')}")

            payload = {}

            if adaptaria_course.get("title") != dislu_course.get("name"):
                payload["title"] = dislu_course.get("name")
                connector_logger.debug(f"Title needs update: {dislu_course.get('name')}")

            if adaptaria_course.get("description") != dislu_course.get("description"):
                payload["description"] = dislu_course.get("description")
                connector_logger.debug(f"Description needs update")

            """ Por ahora no tenemos imagenes en los cursos de Dislu
            if adaptaria_course.get("image") != dislu_course.get("image"):
                payload["image"] = dislu_course.get("image")
            """

            if not payload:
                connector_logger.info(f"No course fields need updating for {entity_id}")
                return

            connector_logger.info(f"Updating course fields in Adaptaria: {list(payload.keys())}")
            response = self.adaptaria_api.request(AdaptariaCourseEndpoints.UPDATE, "patch", payload, {"id": adaptaria_course.get("id")})
            connector_logger.info(f"Course updated successfully in Adaptaria")
            return response
            
        except (ValidationError, APIRequestError) as e:
            connector_logger.error(f"Validation/API error updating course: {str(e)}")
            raise
        except Exception as e:
            connector_logger.error(f"Unexpected error updating course in Adaptaria - ID: {entity_id} | Error: {str(e)}", exc_info=True)
            raise APIRequestError(f"Failed to update course: {str(e)}", entity=entity, entity_id=entity_id)
        

