from ast import List
from math import exp
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
    
    def validate_request(self, institution_id: str):
        dislu_inst = self.dislu_api.request(InstitutionEndpoints.GET, "get", {}, {"id": institution_id})
        if not dislu_inst.get("external_reference"):
            raise PermissionError("forbidden")



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
        #'''
        """
            TODO VER DE INICIALIZAR UNA CUENTA ADMIN EN ADAPTARIA
            # Crear Instituto (como ADMIN)
            POST /institutes/
            → Guarda: instituteId
        """
        try:
            self.dislu_api.request(InstitutionEndpoints.GET, "get", {}, {"id": self.institution_id})
            AdaptariaInstituteTransformer(self.institution_id).run("institution", self.entity_id, "create")
        except Exception as e: print(e)
        
        """
            TODO VER DE INICIALIZAR UNA CUENTA ADMIN EN ADAPTARIA
            # Crear Director (como ADMIN)
            POST /directors/
            Body: { ..., instituteId }
            → Guarda: directorUserId
        """
        try:
            dislu_directors = self.dislu_api.request(InstitutionEndpoints.LIST_ADMINS, "get", {}, {"id": self.institution_id})
            if dislu_directors:
                for director in dislu_directors:
                    director:dict
                    AdaptariaUsersTransformer(self.institution_id).run("admin", director.get("id"), "create")
        except Exception as e: print(e)
        """
            # Crear Student 
            POST /students/
            Headers: { Authorization: "Bearer <sessionToken>" }
            → Guarda: studentUserId
        """
        try:
            dislu_users = self.dislu_api.request(InstitutionEndpoints.LIST_USERS, "get", {}, {"id": self.institution_id})
            if dislu_users:
                for user in dislu_users:
                    user:dict
                    AdaptariaUsersTransformer(self.institution_id).run("student", user.get("id"), "create")
        except Exception as e: print(e)
        
        """
            # Crear Teacher 
            POST /teachers/
            Headers: { Authorization: "Bearer <sessionToken>" }
            → Guarda: teacherUserId
        """
        try:
            dislu_professors = self.dislu_api.request(InstitutionEndpoints.LIST_PROFESSORS, "get", {}, {"id": self.institution_id})
            if dislu_professors:
                for user in dislu_professors:
                    if (self.dislu_api.request(UsersEndpoints.GET, "get", {}, {"id": user.get("user_id")})).get("is_admin"):
                        continue
                    user:dict
                    AdaptariaUsersTransformer(self.institution_id).run("professor", user.get("user_id") +'/' + user.get("course_id"), "update")
        except Exception as e: print(e)

        """
            # Agregar estudiantes al curso
            POST /courses/:courseId/students
            Body: { studentEmails: ["student@..."] }
        """
        try:
            dislu_students = self.dislu_api.request(InstitutionEndpoints.LIST_STUDENTS, "get", {}, {"id": self.institution_id})
            if dislu_students:
                for user in dislu_students:
                    user:dict
                    AdaptariaUsersTransformer(self.institution_id).run("student", user.get("user_id") +'/' + user.get("course_id"), "update")
        except Exception as e: print(e)

        """
            # Crear Section
            POST /courses/:courseId/section
            → Guarda: sectionId
        """
        #'''
        try:
            dislu_roadmaps = self.dislu_api.request(InstitutionEndpoints.LIST_ROADMAPS, "get", {}, {"id": self.institution_id})
            for roadmap in dislu_roadmaps:
                roadmap:dict
                if not (roadmap := roadmap.get("roadmap")):
                    continue
                
                print("ROADMAP")
                print(roadmap)
                AdaptariaSubjectTransformer(self.institution_id).run("roadmap", roadmap.get("id"), "create")
                
                """
                    # Agregar Content
                    POST /courses/:courseId/sections/:sectionId/contents
                    Content-Type: multipart/form-data
                    Body: FormData con file + metadata
                """
                dislu_study_material  = self.dislu_api.request(RoadmapEndpoints.LIST_STUDY_MATERIALS, "get", {}, {"id":  roadmap.get("id")})
                print("STUDYMATERIALL")
                for study_material in dislu_study_material:
                    study_material:dict
                    AdaptariaContentsTransformer(self.institution_id).run("study_material", study_material.get("id"), "create")
        except Exception as e: print(e)


        return True



