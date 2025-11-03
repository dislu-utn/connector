from src.to_dislu.utils.endpoints import CourseEndpoints, DisluEndpoints, InstitutionEndpoints, UsersEndpoints
from src.shared.transformer import TransformedRequest, Transformer
from src.to_adaptaria.utils.endpoints import AdaptariaEndpoints, AdaptariaUserEndpoints

class DisluUsersTransformer(Transformer):

    def run(self, entity:str, entity_id: str, method:str):

        if "create" in method:
            return self.create(entity, entity_id)
        if "update" in method:
            return self.update(entity, entity_id)


        return None 

    def create(self, entity: str, entity_id:str):
        dislu_institution = self.dislu_api.request(InstitutionEndpoints.GET_EXTERNAL, "get", None, {"id": self.institution_id})
        adaptaria_user = self.adaptaria_api.request(AdaptariaUserEndpoints.GET, "get", None, {"id":entity_id})
        adaptaria_hashed_password = self.adaptaria_api.request(AdaptariaUserEndpoints.GET_HASHED_PASSWORD, "get", None, {"id":entity_id})
        payload = {
            "name": adaptaria_user.get("firstName"),
            "surname": adaptaria_user.get("lastName"),
            "email": adaptaria_user.get("email"),
            "external_reference": entity_id,
            "institution_id": dislu_institution.get("id"),
            "is_admin": True if adaptaria_user.get("role") == "DIRECTOR" else False,
            "password": adaptaria_hashed_password
        }
            
        return self.dislu_api.request(UsersEndpoints.CREATE, "post", payload)

    def update(self, entity: str, entity_id:str):
        adaptaria_user = self.adaptaria_api.request(AdaptariaEndpoints.USERS, "get", None, {"id":entity_id})
        dislu_user = self.dislu_api.request(UsersEndpoints.GET_EXTERNAL, "get", None, {"id": entity_id})

        dislu_hashed_password = self.dislu_api.request(UsersEndpoints.GET_HASHED_PASSWORD, "get", None, {"id": dislu_user.get("id")})
        
        adaptaria_hashed_password = self.adaptaria_api.request(AdaptariaUserEndpoints.GET_HASHED_PASSWORD, "get", None, {"id":entity_id})


        payload = {}

        if adaptaria_user.get("firstName") != dislu_user.get("name"):
            payload["name"] = adaptaria_user.get("firstName")

        if adaptaria_user.get("lastName") != dislu_user.get("surname"):
            payload["surname"] = adaptaria_user.get("lastName")

        if adaptaria_user.get("email") != dislu_user.get("email"):
            payload["email"] = adaptaria_user.get("email")

        if adaptaria_hashed_password != dislu_hashed_password:
            payload["password"] = adaptaria_hashed_password

        if adaptaria_user.get("profilePicture") != dislu_user.get("profile_picture"):
            payload["profile_picture"] = adaptaria_user.get("profilePicture")

        if (adaptaria_user.get("role") == "DIRECTOR") and (not dislu_user.get("is_admin")):
            payload["is_admin"] = True
        elif (adaptaria_user.get("role") != "DIRECTOR") and (dislu_user.get("is_admin")):
            payload["is_admin"] = False

        if not payload:
            return

        return self.dislu_api.request(UsersEndpoints.UPDATE, "post", payload)

    def assign_professor(self, entity:str, entity_id:str):
        #Acá el entity_id va a ser "user_id/course_id"
        if "/" in entity_id:
            professor_external_reference, course_external_reference = entity_id.split("/")
            dislu_user = self.dislu_api.request(UsersEndpoints.GET_EXTERNAL, "get", None, {"id": professor_external_reference})
            dislu_course = self.dislu_api.request(CourseEndpoints.GET_EXTERNAL, "get", None, {"id": course_external_reference})
        else:
            dislu_user = ""

        payload = {
            "user_id": dislu_user,
            "course_id": dislu_course
        }

        return self.dislu_api.request(UsersEndpoints.ASSIGN_PROFESSOR, "post", payload)

    def enroll(self, entity:str, entity_id:str):
        #Acá el entity_id va a ser "user_id/course_id"
        student_external_reference, course_external_reference = entity_id.split("/")
        dislu_user = self.dislu_api.request(UsersEndpoints.GET_EXTERNAL, "get", None, {"id": student_external_reference})
        dislu_course = self.dislu_api.request(CourseEndpoints.GET_EXTERNAL, "get", None, {"id": course_external_reference})

        payload = {
            "user_id": dislu_user,
            "course_id": dislu_course
            #matriculation_key?: string;
        }
        
        return self.dislu_api.request(UsersEndpoints.ENROLL, "post", payload)
