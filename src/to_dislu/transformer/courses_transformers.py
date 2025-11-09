from ast import List
import requests
from src.to_dislu.utils.endpoints import CourseEndpoints, DisluEndpoints, InstitutionEndpoints
from src.shared.transformer import TransformedRequest, Transformer
from src.to_adaptaria.utils.endpoints import AdaptariaCourseEndpoints, AdaptariaEndpoints
from src.to_dislu.transformer.users_transformers import DisluUsersTransformer
from src.shared.logger import connector_logger, APIRequestError, ValidationError

class DisluCoursesTransformer(Transformer):

    def run(self, entity:str, entity_id: str, method:str):
        try:
            connector_logger.info(f"Starting DisluCoursesTransformer - Entity: {entity}, ID: {entity_id}, Method: {method}")
            
            if "create" in method:
                result = self.create(entity, entity_id)
                connector_logger.info(f"Successfully created course in Dislu - Entity: {entity}, ID: {entity_id}")
                return result
            if "update" in method:
                result = self.update(entity, entity_id)
                connector_logger.info(f"Successfully updated course in Dislu - Entity: {entity}, ID: {entity_id}")
                return result

            connector_logger.warning(f"No handler found for method: {method}")
            return None
            
        except Exception as e:
            connector_logger.error(f"Error in DisluCoursesTransformer - Entity: {entity}, ID: {entity_id}, Method: {method} | Error: {str(e)}", exc_info=True)
            raise

    def create(self, entity: str, entity_id:str):
        try:
            connector_logger.info(f"Creating course in Dislu from Adaptaria - ID: {entity_id}")
            
            adaptaria_course = self.adaptaria_api.request(AdaptariaCourseEndpoints.GET, "get", {}, {"id":entity_id})
            if not adaptaria_course:
                raise ValidationError("Course not found in Adaptaria", entity=entity, entity_id=entity_id)
            
            connector_logger.debug(f"Retrieved Adaptaria course: {adaptaria_course.get('title')}")
            
            dislu_institution = self.dislu_api.request(InstitutionEndpoints.GET_EXTERNAL, "get", {} ,{"id": self.institution_id})
            if not dislu_institution:
                raise ValidationError(f"Institution not found in Dislu with external ID: {self.institution_id}", entity=entity)

            # Validar campos requeridos
            if not adaptaria_course.get("title"):
                raise ValidationError("Course title is required", entity=entity, entity_id=entity_id)

            payload = {
                "institution_id": dislu_institution.get("id"),
                "name": adaptaria_course.get("title"),
                "description": adaptaria_course.get("description"),
                "matriculation_key": adaptaria_course.get("matriculationCode"),
                "external_reference": adaptaria_course.get("id"),
                "image_link": adaptaria_course.get("image")
            }

            connector_logger.info(f"Creating course in Dislu: {payload['name']}")
            response = self.dislu_api.request(CourseEndpoints.CREATE, "post", payload)
            
            if not response:
                raise APIRequestError("Failed to create course in Dislu", entity=entity, entity_id=entity_id)
            
            connector_logger.info(f"Course created successfully in Dislu")

            #En adaptaria cuando se crea el curso, se le asigna el profesor
            if teacher_id := adaptaria_course.get("teacherUserId"):
                connector_logger.info(f"Assigning teacher {teacher_id} to course")
                DisluUsersTransformer(self.institution_id).assign_professor("teacher", f"{teacher_id}/{entity_id}")

            if students := adaptaria_course.get("students", []):
                connector_logger.info(f"Enrolling {len(students)} students to course")
                for student in students:
                    student: dict
                    DisluUsersTransformer(self.institution_id).enroll("student", f"{student.get('userId')}/{entity_id}")

            return response
            
        except (ValidationError, APIRequestError) as e:
            connector_logger.error(f"Validation/API error creating course: {str(e)}")
            raise
        except Exception as e:
            connector_logger.error(f"Unexpected error creating course in Dislu - ID: {entity_id} | Error: {str(e)}", exc_info=True)
            raise APIRequestError(f"Failed to create course: {str(e)}", entity=entity, entity_id=entity_id)

    def update(self, entity: str, entity_id:str):
        try:
            connector_logger.info(f"Updating course in Dislu from Adaptaria - ID: {entity_id}")
            
            adaptaria_course = self.adaptaria_api.request(AdaptariaEndpoints.COURSES, "get", {},{"id":entity_id})
            if not adaptaria_course:
                raise ValidationError("Course not found in Adaptaria", entity=entity, entity_id=entity_id)
                
            dislu_course = self.dislu_api.request(CourseEndpoints.GET_EXTERNAL, "get", {},{"id": entity_id})
            if not dislu_course:
                raise ValidationError("Course not found in Dislu with external reference", entity=entity, entity_id=entity_id)

            connector_logger.debug(f"Comparing courses - Adaptaria: {adaptaria_course.get('title')}, Dislu: {dislu_course.get('name')}")

            payload = {}

            if adaptaria_course.get("title") != dislu_course.get("name"):
                payload["name"] = adaptaria_course.get("title")
                connector_logger.debug(f"Name needs update: {adaptaria_course.get('title')}")

            if adaptaria_course.get("description") != dislu_course.get("description"):
                payload["description"] = adaptaria_course.get("description")
                connector_logger.debug(f"Description needs update")

            
            if adaptaria_course.get("image") != dislu_course.get("image_link"):
                payload["image"] = adaptaria_course.get("image_link")
            

            if not payload:
                connector_logger.info(f"No course fields need updating for {entity_id}")
                return

            payload["id"] = dislu_course.get("id")
            connector_logger.info(f"Updating course fields in Dislu: {list(payload.keys())}")
            response = self.dislu_api.request(CourseEndpoints.UPDATE, "post", payload)
            connector_logger.info(f"Course updated successfully in Dislu")
            return response
            
        except (ValidationError, APIRequestError) as e:
            connector_logger.error(f"Validation/API error updating course: {str(e)}")
            raise
        except Exception as e:
            connector_logger.error(f"Unexpected error updating course in Dislu - ID: {entity_id} | Error: {str(e)}", exc_info=True)
            raise APIRequestError(f"Failed to update course: {str(e)}", entity=entity, entity_id=entity_id)
        

