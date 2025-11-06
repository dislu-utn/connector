from src.to_dislu.utils.endpoints import CourseEndpoints, DisluEndpoints, InstitutionEndpoints, UsersEndpoints
from src.shared.transformer import TransformedRequest, Transformer
from src.to_adaptaria.utils.endpoints import AdaptariaEndpoints, AdaptariaUserEndpoints
from src.shared.logger import connector_logger, APIRequestError, ValidationError

class DisluUsersTransformer(Transformer):

    def run(self, entity:str, entity_id: str, method:str):
        try:
            connector_logger.info(f"Starting DisluUsersTransformer - Entity: {entity}, ID: {entity_id}, Method: {method}")
            
            if "create" in method:
                # Detectar si el entity_id tiene formato "user_id/course_id"
                # En ese caso, es una asignación de profesor o matrícula de estudiante
                if "/" in entity_id:
                    if entity == "teacher":
                        result = self.assign_professor(entity, entity_id)
                        connector_logger.info(f"Successfully assigned professor in Dislu - ID: {entity_id}")
                        return result
                    elif entity == "student":
                        result = self.enroll(entity, entity_id)
                        connector_logger.info(f"Successfully enrolled student in Dislu - ID: {entity_id}")
                        return result
                    else:
                        raise ValidationError(f"Invalid entity '{entity}' for course assignment format", entity=entity, entity_id=entity_id)
                else:
                    # Crear usuario normal
                    result = self.create(entity, entity_id)
                    connector_logger.info(f"Successfully created user in Dislu - Entity: {entity}, ID: {entity_id}")
                    return result
                    
            if "update" in method:
                result = self.update(entity, entity_id)
                connector_logger.info(f"Successfully updated user in Dislu - Entity: {entity}, ID: {entity_id}")
                return result

            connector_logger.warning(f"No handler found for method: {method}")
            return None
            
        except Exception as e:
            connector_logger.error(f"Error in DisluUsersTransformer - Entity: {entity}, ID: {entity_id}, Method: {method} | Error: {str(e)}", exc_info=True)
            raise 

    def create(self, entity: str, entity_id:str):
        try:
            connector_logger.info(f"Creating user in Dislu from Adaptaria - ID: {entity_id}")
            
            dislu_institution = self.dislu_api.request(InstitutionEndpoints.GET_EXTERNAL, "get", None, {"id": self.institution_id})
            if not dislu_institution:
                raise ValidationError(f"Institution not found in Dislu with external ID: {self.institution_id}", entity=entity)
            
            adaptaria_user = self.adaptaria_api.request(AdaptariaUserEndpoints.GET, "get", None, {"id":entity_id})
            if not adaptaria_user:
                raise ValidationError("User not found in Adaptaria", entity=entity, entity_id=entity_id)
            
            connector_logger.debug(f"Retrieved Adaptaria user: {adaptaria_user.get('email')}")
            
            adaptaria_hashed_password = self.adaptaria_api.request(AdaptariaUserEndpoints.GET_HASHED_PASSWORD, "get", None, {"id":entity_id})
            
            # Validar campos requeridos
            if not adaptaria_user.get("firstName"):
                raise ValidationError("User firstName is required", entity=entity, entity_id=entity_id)
            if not adaptaria_user.get("lastName"):
                raise ValidationError("User lastName is required", entity=entity, entity_id=entity_id)
            if not adaptaria_user.get("email"):
                raise ValidationError("User email is required", entity=entity, entity_id=entity_id)
            
            payload = {
                "name": adaptaria_user.get("firstName"),
                "surname": adaptaria_user.get("lastName"),
                "email": adaptaria_user.get("email"),
                "external_reference": entity_id,
                "institution_id": dislu_institution.get("id"),
                "is_admin": True if adaptaria_user.get("role") == "DIRECTOR" else False,
                "password": adaptaria_hashed_password
            }
            
            connector_logger.info(f"Creating user in Dislu: {payload['email']}")
            response = self.dislu_api.request(UsersEndpoints.CREATE, "post", payload)
            
            if not response:
                raise APIRequestError("Failed to create user in Dislu", entity=entity, entity_id=entity_id)
            
            connector_logger.info(f"User created successfully in Dislu")
            return response
            
        except (ValidationError, APIRequestError) as e:
            connector_logger.error(f"Validation/API error creating user: {str(e)}")
            raise
        except Exception as e:
            connector_logger.error(f"Unexpected error creating user in Dislu - ID: {entity_id} | Error: {str(e)}", exc_info=True)
            raise APIRequestError(f"Failed to create user: {str(e)}", entity=entity, entity_id=entity_id)

    def update(self, entity: str, entity_id:str):
        try:
            connector_logger.info(f"Updating user in Dislu from Adaptaria - ID: {entity_id}")
            
            adaptaria_user = self.adaptaria_api.request(AdaptariaEndpoints.USERS, "get", None, {"id":entity_id})
            if not adaptaria_user:
                raise ValidationError("User not found in Adaptaria", entity=entity, entity_id=entity_id)
                
            dislu_user = self.dislu_api.request(UsersEndpoints.GET_EXTERNAL, "get", None, {"id": entity_id})
            if not dislu_user:
                raise ValidationError("User not found in Dislu with external reference", entity=entity, entity_id=entity_id)

            connector_logger.debug(f"Comparing users - Adaptaria: {adaptaria_user.get('email')}, Dislu: {dislu_user.get('email')}")

            dislu_hashed_password = self.dislu_api.request(UsersEndpoints.GET_HASHED_PASSWORD, "get", None, {"id": dislu_user.get("id")})
            adaptaria_hashed_password = self.adaptaria_api.request(AdaptariaUserEndpoints.GET_HASHED_PASSWORD, "get", None, {"id":entity_id})

            payload = {}

            if adaptaria_user.get("firstName") != dislu_user.get("name"):
                payload["name"] = adaptaria_user.get("firstName")
                connector_logger.debug(f"Name needs update: {adaptaria_user.get('firstName')}")

            if adaptaria_user.get("lastName") != dislu_user.get("surname"):
                payload["surname"] = adaptaria_user.get("lastName")
                connector_logger.debug(f"Surname needs update")

            if adaptaria_user.get("email") != dislu_user.get("email"):
                payload["email"] = adaptaria_user.get("email")
                connector_logger.debug(f"Email needs update: {adaptaria_user.get('email')}")

            if adaptaria_hashed_password != dislu_hashed_password:
                payload["password"] = adaptaria_hashed_password
                connector_logger.debug(f"Password needs update")

            if adaptaria_user.get("profilePicture") != dislu_user.get("profile_picture"):
                payload["profile_picture"] = adaptaria_user.get("profilePicture")
                connector_logger.debug(f"Profile picture needs update")

            if (adaptaria_user.get("role") == "DIRECTOR") and (not dislu_user.get("is_admin")):
                payload["is_admin"] = True
                connector_logger.debug(f"Promoting user to admin")
            elif (adaptaria_user.get("role") != "DIRECTOR") and (dislu_user.get("is_admin")):
                payload["is_admin"] = False
                connector_logger.debug(f"Demoting user from admin")

            if not payload:
                connector_logger.info(f"No user fields need updating for {entity_id}")
                return

            connector_logger.info(f"Updating user fields in Dislu: {list(payload.keys())}")
            response = self.dislu_api.request(UsersEndpoints.UPDATE, "post", payload)
            connector_logger.info(f"User updated successfully in Dislu")
            return response
            
        except (ValidationError, APIRequestError) as e:
            connector_logger.error(f"Validation/API error updating user: {str(e)}")
            raise
        except Exception as e:
            connector_logger.error(f"Unexpected error updating user in Dislu - ID: {entity_id} | Error: {str(e)}", exc_info=True)
            raise APIRequestError(f"Failed to update user: {str(e)}", entity=entity, entity_id=entity_id)

    def assign_professor(self, entity:str, entity_id:str):
        #Acá el entity_id va a ser "user_id/course_id"
        try:
            connector_logger.info(f"Assigning professor in Dislu - ID: {entity_id}")
            
            if "/" not in entity_id:
                raise ValidationError("Invalid entity_id format, expected 'user_id/course_id'", entity=entity, entity_id=entity_id)
            
            professor_external_reference, course_external_reference = entity_id.split("/")
            connector_logger.debug(f"Professor: {professor_external_reference}, Course: {course_external_reference}")
            
            dislu_user = self.dislu_api.request(UsersEndpoints.GET_EXTERNAL, "get", None, {"id": professor_external_reference})
            if not dislu_user:
                raise ValidationError("Professor not found in Dislu with external reference", entity=entity, entity_id=professor_external_reference)
            
            dislu_course = self.dislu_api.request(CourseEndpoints.GET_EXTERNAL, "get", None, {"id": course_external_reference})
            if not dislu_course:
                raise ValidationError("Course not found in Dislu with external reference", entity=entity, entity_id=course_external_reference)

            payload = {
                "user_id": dislu_user.get("id"),
                "course_id": dislu_course.get("id")
            }

            connector_logger.info(f"Assigning professor {dislu_user.get('id')} to course {dislu_course.get('id')}")
            response = self.dislu_api.request(UsersEndpoints.ASSIGN_PROFESSOR, "post", payload)
            connector_logger.info(f"Professor assigned successfully")
            return response
            
        except (ValidationError, APIRequestError) as e:
            connector_logger.error(f"Validation/API error assigning professor: {str(e)}")
            raise
        except Exception as e:
            connector_logger.error(f"Unexpected error assigning professor - ID: {entity_id} | Error: {str(e)}", exc_info=True)
            raise APIRequestError(f"Failed to assign professor: {str(e)}", entity=entity, entity_id=entity_id)

    def enroll(self, entity:str, entity_id:str):
        #Acá el entity_id va a ser "user_id/course_id"
        try:
            connector_logger.info(f"Enrolling student in Dislu - ID: {entity_id}")
            
            if "/" not in entity_id:
                raise ValidationError("Invalid entity_id format, expected 'user_id/course_id'", entity=entity, entity_id=entity_id)
            
            student_external_reference, course_external_reference = entity_id.split("/")
            connector_logger.debug(f"Student: {student_external_reference}, Course: {course_external_reference}")
            
            dislu_user = self.dislu_api.request(UsersEndpoints.GET_EXTERNAL, "get", None, {"id": student_external_reference})
            if not dislu_user:
                raise ValidationError("Student not found in Dislu with external reference", entity=entity, entity_id=student_external_reference)
            
            dislu_course = self.dislu_api.request(CourseEndpoints.GET_EXTERNAL, "get", None, {"id": course_external_reference})
            if not dislu_course:
                raise ValidationError("Course not found in Dislu with external reference", entity=entity, entity_id=course_external_reference)

            payload = {
                "user_id": dislu_user.get("id"),
                "course_id": dislu_course.get("id")
            }
            
            connector_logger.info(f"Enrolling student {dislu_user.get('id')} in course {dislu_course.get('id')}")
            response = self.dislu_api.request(UsersEndpoints.ENROLL, "post", payload)
            connector_logger.info(f"Student enrolled successfully")
            return response
            
        except (ValidationError, APIRequestError) as e:
            connector_logger.error(f"Validation/API error enrolling student: {str(e)}")
            raise
        except Exception as e:
            connector_logger.error(f"Unexpected error enrolling student - ID: {entity_id} | Error: {str(e)}", exc_info=True)
            raise APIRequestError(f"Failed to enroll student: {str(e)}", entity=entity, entity_id=entity_id)
