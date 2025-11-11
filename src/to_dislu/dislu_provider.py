from typing import Any, Dict

import requests
from src.shared.integrate_dto import IntegrateDTO
from src.to_dislu.transformer.courses_transformers import DisluCoursesTransformer
from src.shared.transformer import TransformedRequest
from src.to_dislu.utils.endpoints import DisluEndpoints, InstitutionEndpoints
from src.shared.provider import Provider
from src.to_dislu.transformer.users_transformers import DisluUsersTransformer
from src.to_dislu.transformer.roadmap_transformers import DisluRoadmapTransformer
from src.to_dislu.transformer.study_material_transformers import DisluStudyMaterialTransformer
from src.to_adaptaria.utils.endpoints import AdaptariaCourseEndpoints, AdaptariaEndpoints, AdaptariaInstituteEndpoints, AdaptariaSectionEndpoints
from src.shared.logger import connector_logger


class DisluProvider(Provider):

    def validate_request(self, institution_id: str):
        inst = self.dislu_api.request(InstitutionEndpoints.GET_EXTERNAL, "get", {}, {"id": institution_id})
        if not inst:
            raise PermissionError("forbidden")

    def transform(self): 
        if self.entity == "institute":
            #return DisluInstitutionsTransformer().run(self.entity_id, self.endpoint, self.method, self.payload)
            pass
        if self.entity == "course":
            return DisluCoursesTransformer(self.institution_id).run(self.entity, self.entity_id, self.method)
        if self.entity in ["user","student", "teacher", "director"]:
            return DisluUsersTransformer(self.institution_id).run(self.entity, self.entity_id, self.method)
        if self.entity == "subject":
            return DisluRoadmapTransformer(self.institution_id).run(self.entity, self.entity_id, self.method)
        if self.entity == "content":
            return DisluStudyMaterialTransformer(self.institution_id).run(self.entity, self.entity_id, self.method)

        return None

    def initial_sync(self):
        """
        Sincronización inicial: Adaptaria -> Dislu
        
        Nuevo orden optimizado:
        1. Crear la institución en Dislu
        2. Obtener TODOS los usuarios del instituto y crearlos en Dislu
        3. Obtener todos los cursos e iterar por cada uno:
           3.1. Crear el curso en Dislu
           3.2. Obtener teachers del curso y crear user_x_course con role profesor
           3.3. Obtener students del curso y crear user_x_course con role student  
           3.4. Obtener secciones del curso e iterar:
              3.4.1. Crear la sección como roadmap en Dislu
              3.4.2. Obtener contents de la sección y crear study materials
        """
        from src.to_dislu.transformer.institution_transformers import DisluInstitutionTransformer
        
        connector_logger.info(f"[INITIAL_SYNC] Iniciando sincronización inicial para institución: {self.institution_id}")
        
        # =================================================================
        # PASO 1: Crear Institución en Dislu
        # =================================================================
        connector_logger.info(f"[INITIAL_SYNC] Paso 1: Creando institución en Dislu")
        DisluInstitutionTransformer(self.institution_id).run("institution", self.institution_id, "create")
        connector_logger.info(f"[INITIAL_SYNC] ✓ Institución creada")
        
        # =================================================================
        # PASO 2: Crear TODOS los usuarios del instituto
        # =================================================================
        connector_logger.info(f"[INITIAL_SYNC] Paso 2: Obteniendo y creando todos los usuarios")
        
        # 2.1 Obtener y crear directores (como admins en Dislu)
        connector_logger.info(f"[INITIAL_SYNC] 2.1: Obteniendo directores")
        directors_response = self.adaptaria_api.request(
            AdaptariaInstituteEndpoints.GET_DIRECTORS,
            "get",
            {},
            {"id": self.institution_id}
        )
        adaptaria_directors = directors_response.get("data", []) if isinstance(directors_response, dict) else directors_response
        connector_logger.info(f"[INITIAL_SYNC] Creando {len(adaptaria_directors)} directores en Dislu")
        
        for director in adaptaria_directors:
            director:dict
            connector_logger.info(f"[DIRECTOR] Creando {director} ")
            director_user_id = director.get("user", {}).get("_id")
            if director_user_id:
                DisluUsersTransformer(self.institution_id).run("director", director_user_id, "create")
        
        # 2.2 Obtener y crear estudiantes
        connector_logger.info(f"[INITIAL_SYNC] 2.2: Obteniendo estudiantes")
        students_response = (self.adaptaria_api.request(
            AdaptariaInstituteEndpoints.GET_STUDENTS,
            "get",
            {},
            {"id": self.institution_id}
        ))
        adaptaria_students = students_response.get("data", []) if isinstance(students_response, dict) else students_response
        connector_logger.info(f"[INITIAL_SYNC] Creando {len(adaptaria_students)} estudiantes en Dislu")
        
        for student in adaptaria_students:
            student:dict
            student_id = student.get("id")
            if student_id:
                DisluUsersTransformer(self.institution_id).run("student", student_id, "create")
        
        # 2.3 Obtener y crear profesores (solo el usuario, sin relaciones todavía)
        connector_logger.info(f"[INITIAL_SYNC] 2.3: Obteniendo profesores")
        teachers_response = self.adaptaria_api.request(
            AdaptariaInstituteEndpoints.GET_TEACHERS,
            "get",
            {},
            {"id": self.institution_id}
        )
        adaptaria_teachers = teachers_response.get("data", []) if isinstance(teachers_response, dict) else teachers_response
        connector_logger.info(f"[INITIAL_SYNC] Creando {len(adaptaria_teachers)} profesores en Dislu")
        
        for teacher in adaptaria_teachers:
            teacher_user_id = teacher.get("user", {}).get("id") if isinstance(teacher.get("user"), dict) else teacher.get("user")
            if teacher_user_id:
                # Solo crear el usuario, sin relaciones a cursos todavía
                DisluUsersTransformer(self.institution_id).run("user", teacher_user_id, "create")
        
        connector_logger.info(f"[INITIAL_SYNC] ✓ Todos los usuarios creados")
        
        # =================================================================
        # PASO 3: Iterar por cada curso
        # =================================================================
        connector_logger.info(f"[INITIAL_SYNC] Paso 3: Obteniendo cursos del instituto")
        
        courses_response = self.adaptaria_api.request(
            AdaptariaInstituteEndpoints.GET_COURSES,
            "get",
            {},
            {"id": self.institution_id}
        )
        adaptaria_courses = courses_response.get("data", []) if isinstance(courses_response, dict) else courses_response
        connector_logger.info(f"[INITIAL_SYNC] Procesando {len(adaptaria_courses)} cursos")
        
        for idx, course in enumerate(adaptaria_courses, 1):
            course_id = course.get("id")
            if not course_id:
                continue
            
            connector_logger.info(f"[INITIAL_SYNC] --- Curso {idx}/{len(adaptaria_courses)}: {course_id} ---")
            
            # 3.1 Crear el curso en Dislu
            connector_logger.info(f"[INITIAL_SYNC] 3.1: Creando curso {course_id}")
            DisluCoursesTransformer(self.institution_id).run("course", course_id, "create")
            
            """ (DEPRECATED)
            ## 3.2 Obtener el teacher del curso y crear user_x_course con role profesor
            #connector_logger.info(f"[INITIAL_SYNC] 3.2: Asignando profesor al curso {course_id}")
            #teacher_user_id = course.get("teacherUserId")
            #if teacher_user_id:
            #    entity_id = f"{teacher_user_id}/{course_id}"
            #    DisluUsersTransformer(self.institution_id).run("teacher", entity_id, "create")
            #    connector_logger.info(f"[INITIAL_SYNC] ✓ Profesor {teacher_user_id} asignado")

            # 3.3 Obtener students del curso y crear user_x_course con role student
            connector_logger.info(f"[INITIAL_SYNC] 3.3: Obteniendo estudiantes del curso {course_id}")
            course_students_response = self.adaptaria_api.request(
                AdaptariaCourseEndpoints.GET_STUDENTS,
                "get",
                {},
                {"id": course_id}
            )
            course_students = course_students_response.get("data", []) if isinstance(course_students_response, dict) else course_students_response
            connector_logger.info(f"[INITIAL_SYNC] Matriculando {len(course_students)} estudiantes en curso {course_id}")
            
            for student in course_students:
                student_id = student.get("id")
                if student_id:
                    # Crear la matrícula (user_x_course con role student)
                    entity_id = f"{student_id}/{course_id}"
                    DisluUsersTransformer(self.institution_id).run("student", entity_id, "create")
            """
            
            # 3.4 Obtener secciones del curso e iterar
            connector_logger.info(f"[INITIAL_SYNC] 3.4: Obteniendo secciones del curso {course_id}")
            sections_response = self.adaptaria_api.request(
                AdaptariaCourseEndpoints.GET_SECTIONS,
                "get",
                {},
                {"id": course_id}
            )
            adaptaria_sections = sections_response.get("data", []) if isinstance(sections_response, dict) else sections_response
            connector_logger.info(f"[INITIAL_SYNC] Procesando {len(adaptaria_sections)} secciones")
            
            for section in adaptaria_sections:
                section: dict
                section_id = section.get("id")
                if not section_id:
                    continue
                
                # 3.4.1 Crear la sección como roadmap
                connector_logger.info(f"[INITIAL_SYNC] 3.4.1: Creando roadmap para sección {section_id}")
                DisluRoadmapTransformer(self.institution_id).run("subject", course_id + '/' + section_id, "create")
                
                # 3.4.2 Obtener contents y crear study materials
                connector_logger.info(f"[INITIAL_SYNC] 3.4.2: Obteniendo contenidos de sección {section_id}")
                contents_response = self.adaptaria_api.request(
                    AdaptariaSectionEndpoints.GET_CONTENTS,
                    "get",
                    {},
                    {"id": section_id}
                )
                adaptaria_contents = contents_response.get("data", []) if isinstance(contents_response, dict) else contents_response
                connector_logger.info(f"[INITIAL_SYNC] Creando {len(adaptaria_contents)} study materials")
                
                for content in adaptaria_contents:
                    content_id = content.get("id")
                    if content_id:
                        DisluStudyMaterialTransformer(self.institution_id).run("content", content_id, "create")
            
            connector_logger.info(f"[INITIAL_SYNC] ✓ Curso {course_id} completado")
        
        connector_logger.info(f"[INITIAL_SYNC] ✓✓✓ Sincronización inicial completada para institución: {self.institution_id} ✓✓✓")
        #raise Exception("stop")
        return True
