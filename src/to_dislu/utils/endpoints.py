from ast import Constant
from enum import Enum
from http.client import HTTPResponse
import os
from dotenv import load_dotenv

import requests
import re

from urllib3.util import url

load_dotenv()

class DisluAPI:

    def __init__(self):
        # TODO: En producción cambiar a HTTPS
        self.base_url = os.getenv("DISLU_BASE_URL", "http://localhost:4000/api")
        self.secret = os.getenv("DISLU_SECRET")
        
        if not self.secret:
            raise ValueError("DISLU_SECRET no está configurado en las variables de entorno")
        
        # Advertencia si se usa HTTP en producción
        if not self.base_url.startswith("https://") and "localhost" not in self.base_url:
            print("[WARNING] DisluAPI: Usando HTTP en lugar de HTTPS. Esto NO es seguro para producción.")

    def request(self, endpoint: Constant, method: str, payload={}, url_params={}, files=None,**kwargs) -> dict:
        endpoint = self.base_url + endpoint.value
        id_in_url = ":id" in endpoint
        if url_params:
            endpoint = self.fill_url(endpoint, url_params)

        # Usar el DISLU_SECRET en el header Authorization
        headers = kwargs.get('headers', {})
        headers['authorization'] = f'Bearer {self.secret}'
        kwargs['headers'] = headers
        
        method = method.lower()
        if method == 'post':
            print(f"[DisluAPI] POST {endpoint} | Headers: {kwargs.get('headers', {})} | Params: {url_params} | Payload: {payload}")
            response = requests.post(endpoint, json=payload, files=files, **kwargs)
        elif method == 'get':
            if "id" in url_params and not id_in_url:
                endpoint += f"/{url_params["id"]}"
            elif "id" in payload and not id_in_url:
                endpoint += f"/{payload["id"]}"
            response = requests.get(endpoint, **kwargs)
        elif method == 'put':
            response = requests.put(endpoint, json=payload, **kwargs)
        elif method == 'delete':
            response = requests.delete(endpoint, json=payload, **kwargs)
        elif method == 'patch':
            response = requests.patch(endpoint, json=payload, **kwargs)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        print(f"[DisluAPI] {method.upper()} {endpoint} - Response: {response.status_code}")

        if not response.ok:
            response.raise_for_status()

        # Manejar respuestas sin contenido o sin JSON
        if response.status_code == 204 or not response.content:
            return {}
        
        try:
            return response.json()
        except requests.exceptions.JSONDecodeError:
            # Si la respuesta no es JSON, retornar objeto vacío
            return {}

    def update_external_reference(self, endpoint, id, external_id):
        payload = {"id":id, "external_reference":external_id}
        return self.request(endpoint, 'post', payload)

    
    def fill_url(self, url, params):
        return re.sub(r":(\w+)", lambda m: str(params.get(m.group(1), m.group(0))), url)

class DisluEndpoints(Enum):
    INSTITUTIONS = "/institution"
    USERS = "/users"
    USER_X_COURSE = "/user_x_course"
    COURSES = "/courses"
    ROADMAPS = "/roadmaps"
    STUDY_MATERIALS = ""

class InstitutionEndpoints(Enum):
    CREATE = "/connector" + DisluEndpoints.INSTITUTIONS.value + "/create"
    UPDATE = "/connector" + DisluEndpoints.INSTITUTIONS.value + "/update"
    GET = DisluEndpoints.INSTITUTIONS.value
    GET_EXTERNAL = DisluEndpoints.INSTITUTIONS.value + "/get_external/:id" #Done
    LIST_ADMINS = DisluEndpoints.INSTITUTIONS.value + "/:id/admins"
    LIST_USERS = DisluEndpoints.INSTITUTIONS.value + "/:id/users"
    LIST_PROFESSORS = DisluEndpoints.INSTITUTIONS.value + "/:id/professors"
    LIST_STUDENTS = DisluEndpoints.INSTITUTIONS.value + "/:id/students"
    LIST_ROADMAPS = DisluEndpoints.INSTITUTIONS.value + "/:id/roadmaps"

class CourseEndpoints(Enum):
    CREATE = "/connector" + DisluEndpoints.COURSES.value + "/create"
    UPDATE = "/connector" + DisluEndpoints.COURSES.value + "/update"
    GET = DisluEndpoints.COURSES.value + "/:id"
    GET_EXTERNAL = DisluEndpoints.COURSES.value + "/get_external/:id" #Done


class UsersEndpoints(Enum):
    CREATE = "/connector" + DisluEndpoints.USERS.value + "/create"
    UPDATE = "/connector" + DisluEndpoints.USERS.value + "/update"
    GET = DisluEndpoints.USERS.value + "/:id"
    GET_EXTERNAL = DisluEndpoints.USERS.value + "/get_external/:id" #Done
    GET_HASHED_PASSWORD = "/connector" + DisluEndpoints.USERS.value + "/get_hashed_password"
    ENROLL = "/connector" + DisluEndpoints.USERS.value + "/enroll" 
    ASSIGN_PROFESSOR = "/connector" + DisluEndpoints.USERS.value + "/assign_professor" 

class UsersXCourseEndpoints(Enum):
    GET_PROFESSOR_BY_EXTERNAL_ID = DisluEndpoints.USER_X_COURSE.value + "/get_professor_by_external_id"
    ENROLLED_COURSES = DisluEndpoints.USER_X_COURSE.value + "/courses"

class RoadmapEndpoints(Enum):
    CREATE = "/connector" + DisluEndpoints.ROADMAPS.value + "/create"
    UPDATE = "/connector" + DisluEndpoints.ROADMAPS.value + "/update"
    GET_EXTERNAL = DisluEndpoints.ROADMAPS.value + "/get_external/:id" #Done
    GET = DisluEndpoints.ROADMAPS.value + "/:id"
    LIST_STUDY_MATERIALS = DisluEndpoints.ROADMAPS.value + "/:id/materials"

class StudyMaterialEndpoints(Enum):
    CREATE = "/connector" + DisluEndpoints.ROADMAPS.value + "/upload_study_material"
    GET = "/connector/study_material/:id"
