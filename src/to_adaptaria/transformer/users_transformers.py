from random import randint
from time import sleep
from jinja2 import Undefined
from src.to_dislu.utils.endpoints import CourseEndpoints, DisluEndpoints, InstitutionEndpoints, UsersEndpoints, UsersXCourseEndpoints
from src.shared.transformer import TransformedRequest, Transformer
from src.to_adaptaria.utils.endpoints import AdaptariaCourseEndpoints, AdaptariaDirectorEndponints, AdaptariaEndpoints, AdaptariaStudentEndponints, AdaptariaUserEndpoints
from src.shared.logger import connector_logger, APIRequestError, MappingError, ValidationError

class AdaptariaUsersTransformer(Transformer):

    def run(self, entity:str, entity_id: str, method:str):
        try:
            connector_logger.info(f"Starting AdaptariaUsersTransformer - Entity: {entity}, ID: {entity_id}, Method: {method}")
            
            if "create" in method:
                result = self.create(entity, entity_id)
                connector_logger.info(f"Successfully created user in Adaptaria - Entity: {entity}, ID: {entity_id}")
                return result
            if "update" in method:
                result = self.update(entity, entity_id)
                connector_logger.info(f"Successfully updated user in Adaptaria - Entity: {entity}, ID: {entity_id}")
                return result

            connector_logger.warning(f"No handler found for method: {method}")
            return None
        except Exception as e:
            connector_logger.error(f"Error in AdaptariaUsersTransformer - Entity: {entity}, ID: {entity_id}, Method: {method} | Error: {str(e)}", exc_info=True)
            raise 

    def create(self, entity: str, entity_id:str):        
        #Crear usuario de 0, lo creo como student
        try:
            connector_logger.info(f"Creating user in Adaptaria - Entity: {entity}, ID: {entity_id}")
            
            # Obtener datos del usuario de Dislu
            dislu_user = self.dislu_api.request(UsersEndpoints.GET, "get", {}, {"id": entity_id})
            if not dislu_user:
                raise ValidationError(f"User not found in Dislu", entity=entity, entity_id=entity_id)
            
            if dislu_user.get("external_reference"):
                 raise ValidationError("User in Dislu already has an external reference", entity=entity, entity_id=entity_id)

            connector_logger.debug(f"Retrieved Dislu user: {dislu_user.get('email')}")
            
            dislu_hashed_password = self.dislu_api.request(UsersEndpoints.GET_HASHED_PASSWORD, "get", {}, {"id": entity_id}).get("password", "")

            # Validar campos requeridos
            if not dislu_user.get("name"):
                raise ValidationError("User name is required", entity=entity, entity_id=entity_id)
            if not dislu_user.get("surname"):
                raise ValidationError("User surname is required", entity=entity, entity_id=entity_id)
            if not dislu_user.get("email"):
                raise ValidationError("User email is required", entity=entity, entity_id=entity_id)
            
            dislu_institution = self.dislu_api.request(InstitutionEndpoints.GET, "get", {}, {"id": self.institution_id})["external_reference"]
            print()
            if entity == "student":
                connector_logger.info(f"Creating student in Adaptaria: {dislu_user.get('email')}")
                response = self.adaptaria_api.request(
                    AdaptariaStudentEndponints.CREATE,
                    "post",
                    {
                        "firstName": dislu_user.get("name"),
                        "lastName": dislu_user.get("surname"),
                        "email": dislu_user.get("email"),
                        "institute": {
                            "id": dislu_institution
                        },
                        "password": dislu_hashed_password,
                        "document":{
                            "type":"DNI",
                            "number": str(randint(10000000,99999999))
                        }
                    }
                )
            elif entity == "admin":
                connector_logger.info(f"Creating director in Adaptaria: {dislu_user.get('email')}")
                response = self.adaptaria_api.request(
                    AdaptariaDirectorEndponints.CREATE,
                    "post",
                    {
                        "firstName": dislu_user.get("name", ""),
                        "lastName": dislu_user.get("surname", ""),
                        "email": dislu_user.get("email", ""),
                        "institute": {
                            "id": dislu_institution
                        },
                        "password": dislu_hashed_password,
                        "document":{
                            "type":"DNI",
                            "number": str(randint(10000000,99999999))
                        }
                    }
                )
            else:
                raise ValidationError(f"Invalid entity type: {entity}", entity=entity, entity_id=entity_id)

            if not response or not response.get("id"):
                error_detail = response.get("error") if response else None
                raise APIRequestError(
                    f"Failed to create user in Adaptaria - no ID returned"
                    + (f". Error: {error_detail}" if error_detail else ""),
                    entity=entity,
                    entity_id=entity_id
                )

            connector_logger.info(f"User created successfully in Adaptaria - Adaptaria ID: {response.get('id')}")

            # Actualizar referencia externa en Dislu
            self.dislu_api.update_external_reference(
                UsersEndpoints.UPDATE, 
                dislu_user.get("id"), 
                response.get("id")
            )
            
            connector_logger.info(f"External reference updated in Dislu for user {entity_id}")

            return response
            
        except (ValidationError, APIRequestError) as e:
            connector_logger.error(f"Validation/API error creating user: {str(e)}")
            raise
        except Exception as e:
            connector_logger.error(f"Unexpected error creating user in Adaptaria - Entity: {entity}, ID: {entity_id} | Error: {str(e)}", exc_info=True)
            raise APIRequestError(f"Failed to create user: {str(e)}", entity=entity, entity_id=entity_id)


    def update(self, entity: str, entity_id:str):
        #Acá el entity_id va a ser "user_id/course_id"
        try:
            response = None
            connector_logger.info(f"Updating user in Adaptaria - Entity: {entity}, ID: {entity_id}")
            
            if "/" in entity_id:
                user_dislu_id, course_dislu_id = entity_id.split("/")
                dislu_course = self.dislu_api.request(CourseEndpoints.GET, "get", {}, {"id": course_dislu_id})
                if not dislu_course:
                    raise ValidationError(f"Course not found in Dislu", entity=entity, entity_id=course_dislu_id)
            else:
                user_dislu_id = entity_id

            connector_logger.info(f"Parsed IDs - User: {user_dislu_id}, Course: {course_dislu_id}")
            
            # Obtener datos de Dislu
            dislu_user = self.dislu_api.request(UsersEndpoints.GET, "get", {}, {"id": user_dislu_id})
            if not dislu_user:
                raise ValidationError(f"User not found in Dislu", entity=entity, entity_id=user_dislu_id)
            

            # Obtener referencias externas
            if not dislu_user.get("external_reference"):
                raise ValidationError("User has no external reference in Adaptaria", entity=entity, entity_id=user_dislu_id)
            
            # Obtener datos de Adaptaria
            adaptaria_user = self.adaptaria_api.request(AdaptariaEndpoints.USERS, "get", {"id": dislu_user.get("external_reference")})
            if not adaptaria_user:
                raise APIRequestError("User not found in Adaptaria", entity=entity, entity_id=dislu_user.get("external_reference"))
                
            adaptaria_role = adaptaria_user.get("role")
            connector_logger.info(f"Adaptaria user role: {adaptaria_role}")

            if (entity == "user"):
                connector_logger.info(f"Updating user fields for {dislu_user.get('email')}")
                return self.update_user_fields(dislu_user, adaptaria_user)

            if (entity == "professor") and (adaptaria_role == "STUDENT"):
                #Convertir a profesor
                connector_logger.info(f"Converting student to TEACHER: {dislu_user.get('email')}")
                response = self.adaptaria_api.request(
                    AdaptariaUserEndpoints.UPDATE_ROLE,
                    "patch",
                    {
                        "newRole": "TEACHER"
                    }, 
                    {
                        "userId": dislu_user.get("external_reference")
                    }
                )
                connector_logger.info(f"User role updated to TEACHER successfully")

                if not dislu_course.get("external_reference"):
                    if not (image_link := dislu_course.get("image_link")):
                        image_link = "https://picsum.photos/300/200"
                    response = self.adaptaria_api.request(
                        AdaptariaCourseEndpoints.CREATE,
                        "post",
                        {
                            "title": dislu_course.get("name") if dislu_course.get("name") else "Default course" ,
                            "description": dislu_course.get("description") if dislu_course.get("description") else "Default description",
                            "matriculationCode": dislu_course.get("matriculation_key"),
                            "teacherUserId": adaptaria_user.get("id"),
                            "image": image_link
                        }
                    )
                    if not response or not response.get("id"):
                        raise APIRequestError("Failed to create course in Adaptaria", entity=entity, entity_id=dislu_course.get("id"))
                    connector_logger.info(f"Course created in Adaptaria - ID: {response.get('id')}")

                    self.dislu_api.update_external_reference(
                        CourseEndpoints.UPDATE, 
                        dislu_course.get("id"), 
                        response.get("id")
                    )
                    dislu_course["external_reference"] = response.get("id")
                    connector_logger.info(f"External reference updated in Dislu for course {course_dislu_id}")
                    #sleep(1)


            adaptaria_course = self.adaptaria_api.request(AdaptariaCourseEndpoints.GET, "get", {"id": dislu_course.get("external_reference")})
            if not adaptaria_course:
                raise APIRequestError("Course not found in Adaptaria", entity=entity, entity_id=dislu_course.get("external_reference"))


            if (entity == "admin"):
                #Convertir a director
                connector_logger.info(f"Converting user to DIRECTOR: {dislu_user.get('email')}")
                response = self.adaptaria_api.request(
                    AdaptariaUserEndpoints.UPDATE_ROLE,
                    "patch",
                    {
                        "newRole": "DIRECTOR"
                    }, 
                    {
                        "userId": dislu_user.get("external_reference")
                    }
                )
                connector_logger.info(f"User role updated to DIRECTOR successfully")
                return response

            if (
                (entity == "student" and adaptaria_role == "STUDENT") or
                (entity == "professor" and adaptaria_course.get("teacherUserId") and adaptaria_role == "STUDENT")
            ):

                #Usuario se enroló a un curso o el profesor ya tiene un curso
                connector_logger.info(f"Adding student {dislu_user.get('email')} to course {dislu_course.get('name')}")
                response = self.adaptaria_api.request(
                    AdaptariaCourseEndpoints.ADD_STUDENT,
                    "post",
                    {
                        "studentEmails": [dislu_user.get("email")]
                    },
                    {
                        "courseId": dislu_course.get("external_reference")
                    }
                )
                connector_logger.info(f"Student added to course successfully")
                return response
            
            return response
                
        except (ValidationError, APIRequestError) as e:
            connector_logger.error(f"Validation/API error updating user: {str(e)}")
            raise
        except Exception as e:
            connector_logger.error(f"Unexpected error updating user in Adaptaria - Entity: {entity}, ID: {entity_id} | Error: {str(e)}", exc_info=True)
            raise APIRequestError(f"Failed to update user: {str(e)}", entity=entity, entity_id=entity_id)

    def update_user_fields(self, dislu_user: dict, adaptaria_user: dict):
        try:
            connector_logger.debug(f"Checking user fields to update for {dislu_user.get('email')}")
            
            payload = {}
            if dislu_user.get("profile_picture") != adaptaria_user.get("profilePicture"):
                payload["profilePicture"] = dislu_user.get("profile_picture")
                connector_logger.debug(f"Profile picture needs update")

            if not payload:
                connector_logger.debug(f"No user fields need updating")
                return None
            
            payload["userId"] = adaptaria_user.get("id")

            connector_logger.info(f"Updating user fields in Adaptaria for {dislu_user.get('email')}")
            response = self.adaptaria_api.request(
                AdaptariaUserEndpoints.UPDATE,
                "patch",
                payload
            )
            connector_logger.info(f"User fields updated successfully")
            return response
            
        except Exception as e:
            connector_logger.error(f"Error updating user fields: {str(e)}", exc_info=True)
            raise APIRequestError(f"Failed to update user fields: {str(e)}")

