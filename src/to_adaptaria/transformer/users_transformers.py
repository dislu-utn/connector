from src.to_dislu.utils.endpoints import CourseEndpoints, DisluEndpoints, InstitutionEndpoints, UsersEndpoints, UsersXCourseEndpoints
from src.shared.transformer import TransformedRequest, Transformer
from src.to_adaptaria.utils.endpoints import AdaptariaCourseEndpoints, AdaptariaEndpoints, AdaptariaStudentEndponints, AdaptariaUserEndpoints

class AdaptariaUsersTransformer(Transformer):

    def run(self, entity:str, entity_id: str, method:str):

        if "create" in method:
            return self.create(entity, entity_id)
        if "update" in method:
            return self.update(entity, entity_id)

        return None 

    def create(self, entity: str, entity_id:str):        
        #Crear usuario de 0, lo creo como student
    
        dislu_user = self.dislu_api.request(UsersEndpoints.GET, "get", None, {"id": entity_id})
        response = self.adaptaria_api.request(
            AdaptariaStudentEndponints.CREATE,
            "post",
            {
                "firstName": dislu_user.get("name"),
                "lastName": dislu_user.get("surname"),
                "email": dislu_user.get("email"),
            }
        )
        self.dislu_api.update_external_reference(
            UsersEndpoints.UPDATE, 
            dislu_user.get("id"), 
            response.get("id")
            )

        return response


    def update(self, entity: str, entity_id:str):
        #Acá el entity_id va a ser "user_id/course_id"

        user_dislu_id, course_dislu_id = entity_id.split("/")
        dislu_user = self.dislu_api.request(UsersEndpoints.GET, "get", None, {"id": user_dislu_id})
        dislu_course = self.dislu_api.request(CourseEndpoints.GET, "get", None, {"id": course_dislu_id})


        adaptaria_user = self.adaptaria_api.request(AdaptariaEndpoints.USERS, "get", {"id": dislu_user.get("external_reference")})
        adaptaria_course = self.adaptaria_api.request(AdaptariaEndpoints.COURSES, "get", {"id": dislu_user.get("external_reference")})

        adaptaria_role = adaptaria_user.get("role")

        if (entity == "user"):
            return self.update_user_fields(dislu_user, adaptaria_user)

        if (entity == "admin"):
            #Convertir a profesor
            self.adaptaria_api.request(
                AdaptariaUserEndpoints.UPDATE_ROLE,
                "patch",
                {
                    "newRole": "DIRECTOR"
                }, 
                {
                    "userId": adaptaria_user.get("id")
                }
            )

        if (
            (entity == "student" and adaptaria_role == "STUDENT") or
            (entity == "professor" and adaptaria_course.get("teacherUserId"))
        ):
            #Usuario se enroló a un curso o el profesor ya tiene un curso
            response = self.adaptaria_api.request(
                AdaptariaCourseEndpoints.ADD_STUDENT,
                "post",
                {
                    "studentEmails": [dislu_user.get("email")]
                },
                {
                    "courseId": course_dislu_id
                }
            )

            return response
        

        if (entity == "professor") and (adaptaria_role == "STUDENT"):
            #Convertir a profesor
            self.adaptaria_api.request(
                AdaptariaUserEndpoints.UPDATE_ROLE,
                "patch",
                {
                    "newRole": "TEACHER"
                }, 
                {
                    "userId": adaptaria_user.get("id")
                }
            )


        if (entity == "professor") and (adaptaria_role == "TEACHER"):
            response = self.adaptaria_api.request(
                AdaptariaCourseEndpoints.CREATE,
                "create",
                {
                    "title": dislu_course.get("name"),
                    "description": dislu_course.get("description"),
                    "matriculationCode": dislu_course.get("matriculation_key"),
                    "teacherUserId": adaptaria_user.get("id")
                }
            )

            self.dislu_api.update_external_reference(
                CourseEndpoints.UPDATE, 
                dislu_course.get("id"), 
                response.get("id")
            )
            
            return response

    def update_user_fields(self, dislu_user: dict, adaptaria_user: dict):

        payload = {}
        if dislu_user.get("profile_picture") != adaptaria_user.get("profilePicture"):
            payload["profilePicture"] = dislu_user.get("profile_picture")

        if not payload:
            return None
        
        payload["userId"] = adaptaria_user.get("id")

        return self.adaptaria_api.request(
            AdaptariaUserEndpoints.UPDATE,
            "patch",
            payload
        )

