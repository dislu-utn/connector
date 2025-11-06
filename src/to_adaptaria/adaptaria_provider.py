from flask import request
import requests
from src.shared.provider import Provider
from src.to_adaptaria.transformer.courses_transformer import AdaptariaCoursesTransformer
from src.to_adaptaria.transformer.users_transformers import AdaptariaUsersTransformer
from src.to_adaptaria.transformer.contents_transformer import AdaptariaContentsTransformer
from src.to_adaptaria.transformer.subject_transformers import AdaptariaSubjectTransformer
from src.to_adaptaria.transformer.institute_transformer import AdaptariaInstituteTransformer
from src.to_adaptaria.utils.endpoints import AdaptariaEndpoints, AdaptariaInstituteEndpoints
from src.to_dislu.transformer.courses_transformers import DisluCoursesTransformer
from src.to_dislu.transformer.institution_transformers import DisluInstitutionTransformer
from src.to_dislu.utils.endpoints import InstitutionEndpoints, RoadmapEndpoints, UsersEndpoints


class AdaptariaProvider(Provider):
    
    def transform(self): 
        if self.entity == "course":
            return AdaptariaCoursesTransformer(self.institution_id).run(self.entity, self.entity_id, self.method)
        if self.entity == "roadmap":
            return AdaptariaSubjectTransformer(self.institution_id).run(self.entity, self.entity_id, self.method)
        if self.entity == "study_material":
            return AdaptariaContentsTransformer(self.institution_id).run(self.entity, self.entity_id, self.method)
        if self.entity in ["user", "student", "professor", "admin"]:
            return AdaptariaUsersTransformer(self.institution_id).run(self.entity, self.entity_id, self.method)
        if self.entity == "institution":
            return AdaptariaInstituteTransformer(self.institution_id).run(self.entity, self.entity_id, self.method)
        if self.entity == "subject":
            return AdaptariaSubjectTransformer(self.institution_id).run(self.entity, self.entity_id, self.method)
              
        return None

    def initial_sync(self):
        """
            TODO VER DE INICIALIZAR UNA CUENTA ADMIN EN ADAPTARIA
            # Crear Instituto (como ADMIN)
            POST /institutes/
            → Guarda: instituteId
        """

        self.dislu_api.request(InstitutionEndpoints.GET, "get", None, {"id": self.institution_id})
        AdaptariaInstituteTransformer(self.institution_id).run("institution", self.entity_id, "create")
        
        """
            TODO VER DE INICIALIZAR UNA CUENTA ADMIN EN ADAPTARIA
            # Crear Director (como ADMIN)
            POST /directors/
            Body: { ..., instituteId }
            → Guarda: directorUserId
        """
        dislu_directors = self.dislu_api.request(InstitutionEndpoints.LIST_ADMINS, "get", None, {"id": self.institution_id})
        if dislu_directors:
            for director in dislu_directors:
                director:dict
                AdaptariaUsersTransformer(self.institution_id).run("admin", director.get("id"), "create")

        """
            # Crear Student 
            POST /students/
            Headers: { Authorization: "Bearer <sessionToken>" }
            → Guarda: studentUserId
        """
        dislu_users = self.dislu_api.request(InstitutionEndpoints.LIST_USERS, "get", None, {"id": self.institution_id})
        if dislu_users:
            for user in dislu_users:
                user:dict
                AdaptariaUsersTransformer(self.institution_id).run("student", user.get("id"), "create")

        """
            # Crear Teacher 
            POST /teachers/
            Headers: { Authorization: "Bearer <sessionToken>" }
            → Guarda: teacherUserId
        """
        dislu_professors = self.dislu_api.request(InstitutionEndpoints.LIST_PROFESSORS, "get", None, {"id": self.institution_id})
        if dislu_professors:
            for user in dislu_professors:
                user:dict
                AdaptariaUsersTransformer(self.institution_id).run("professor", user.get("user_id") +'/' + user.get("course_id"), "update")

        """
            # Agregar estudiantes al curso
            POST /courses/:courseId/students
            Body: { studentEmails: ["student@..."] }
        """
        dislu_students = self.dislu_api.request(InstitutionEndpoints.LIST_STUDENTS, "get", None, {"id": self.institution_id})
        if dislu_students:
            for user in dislu_students:
                user:dict
                AdaptariaUsersTransformer(self.institution_id).run("professor", user.get("user_id") +'/' + user.get("course_id"), "update")

        """
            # Crear Section
            POST /courses/:courseId/section
            → Guarda: sectionId
        """
        dislu_roadmaps = self.dislu_api.request(InstitutionEndpoints.LIST_ROADMAPS, "get", None, {"id": self.institution_id})
        for roadmap in dislu_roadmaps:
            roadmap:dict
            AdaptariaSubjectTransformer(self.institution_id).run("roadmap", roadmap.get("id"), "create")
            
            """
                # Agregar Content
                POST /courses/:courseId/sections/:sectionId/contents
                Content-Type: multipart/form-data
                Body: FormData con file + metadata
            """
            dislu_study_material = self.dislu_api.request(RoadmapEndpoints.LIST_STUDY_MATERIALS, "get", None, {"id":  roadmap.get("id")})
            for study_material in dislu_study_material:
                study_material:dict
                AdaptariaContentsTransformer(self.institution_id).run("study_material", study_material.get("id"), "create")


        return True



