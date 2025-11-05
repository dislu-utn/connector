from src.shared.provider import Provider
from src.to_adaptaria.transformer.courses_transformer import AdaptariaCoursesTransformer
from src.to_adaptaria.transformer.users_transformers import AdaptariaUsersTransformer
from src.to_adaptaria.transformer.contents_transformer import AdaptariaContentsTransformer
from src.to_adaptaria.transformer.subject_transformers import AdaptariaSubjectTransformer
from to_adaptaria.utils.endpoints import AdaptariaEndpoints
from to_dislu.transformer.courses_transformers import DisluCoursesTransformer


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
            
        return None

    def initial_sync(self):
        """
        DE DISLU A ADAPTARIA:

            # 2. Crear Director (como ADMIN)
            POST /directors/
            Body: { ..., instituteId }
            → Guarda: directorUserId

            # 3. Login como Director
            POST /auth/login
            Body: { email: "director@...", password: "..." }
            → Guarda: sessionToken

            # 4. Crear Teacher (como DIRECTOR autenticado)
            POST /teachers/
            Headers: { Authorization: "Bearer <sessionToken>" }
            → Guarda: teacherUserId

            # 5. Crear Student (como DIRECTOR autenticado)
            POST /students/
            Headers: { Authorization: "Bearer <sessionToken>" }
            → Guarda: studentUserId

            # 6. Login como Teacher
            POST /auth/login
            Body: { email: "teacher@...", password: "..." }
            → Guarda: teacherSessionToken

            # 7. Crear Course (como TEACHER autenticado)
            POST /courses/
            Headers: { Authorization: "Bearer <teacherSessionToken>" }
            → Guarda: courseId

            # 8. Agregar estudiantes al curso
            POST /courses/:courseId/students
            Body: { studentEmails: ["student@..."] }

            # 9. Crear Section
            POST /courses/:courseId/section
            → Guarda: sectionId

            # 10. Agregar Content
            POST /courses/:courseId/sections/:sectionId/contents
            Content-Type: multipart/form-data
            Body: FormData con file + metadata
        """

        """
            # 1. Crear Instituto (como ADMIN)
            POST /institutes/
            → Guarda: instituteId
        """
        adaptaria_institute = self.adaptaria_api.request(AdaptariaEndpoints.INSTITUTES, "get", None, {"id": self.institution_id})
        DisluInstitutionsTransformer(self.institution_id).run(self.entity, self.entity_id, self.method)
        
        pass



