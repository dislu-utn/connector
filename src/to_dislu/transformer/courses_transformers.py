from ast import List
import requests
from src.to_dislu.utils.endpoints import CourseEndpoints, DisluEndpoints, InstitutionEndpoints
from src.shared.transformer import TransformedRequest, Transformer
from src.to_adaptaria.utils.endpoints import AdaptariaEndpoints
from to_dislu.transformer.users_transformers import DisluUsersTransformer
from to_dislu.transformer.users_x_courses_transformers import DisluUsersXCoursesTransformer

class DisluCoursesTransformer(Transformer):

    def run(self, entity:str, entity_id: str, method:str):

        if "create" in method:
            return self.create(entity, entity_id)
        if "update" in method:
            return self.update(entity, entity_id)

        return None 

    def create(self, entity: str, entity_id:str):
        adaptaria_course = self.adaptaria_api.request(AdaptariaEndpoints.COURSES, "get", None, {"id":entity_id})
        dislu_institution = self.dislu_api.request(InstitutionEndpoints.GET_EXTERNAL, "get", None,{"id": self.institution_id})

        payload = {
            "institution": dislu_institution.get("id"),
            "name": adaptaria_course.get("title"),
            "description": adaptaria_course.get("description"),
            "matriculation_key": adaptaria_course.get("matriculationCode"),
            "external_reference": adaptaria_course.get("id"),
            #"image": adaptaria_course.get("image")
        }

        response = self.dislu_api.request(CourseEndpoints.CREATE, "post", payload)

        #En adaptaria cuando se crea el curso, se le asigna el profesor
        if teacher_id := adaptaria_course.get("teacherUserId"):
            DisluUsersTransformer().assign_professor("teacher", f"{teacher_id}/{entity_id}")

        if students := adaptaria_course.get("students", []):
            for student in students:
                student: dict
                DisluUsersTransformer().enroll("student", f"{student.get('userId')}/{entity_id}")

        return response

    def update(self, entity: str, entity_id:str):
        adaptaria_course = self.adaptaria_api.request(AdaptariaEndpoints.COURSES, "get", None,{"id":entity_id})
        dislu_course = self.dislu_api.request(CourseEndpoints.GET_EXTERNAL, "get", None,{"id": entity_id})

        payload = {}

        if adaptaria_course.get("title") != dislu_course.get("name"):
            payload["name"] = dislu_course.get("title")

        if adaptaria_course.get("description") != dislu_course.get("description"):
            payload["description"] = dislu_course.get("description")

        """ Por ahora no tenemos imagenes en los cursos de Dislu
        if adaptaria_course.get("image") != dislu_course.get("image"):
            payload["image"] = dislu_course.get("image")
        """

        if not payload:
            return

        return self.dislu_api.request(CourseEndpoints.UPDATE, "post", payload)
        

