from ast import Constant
from enum import Enum
import re
import os
from dotenv import load_dotenv
import requests
from src.shared.logger import connector_logger, APIRequestError

# Cargar variables de entorno una sola vez al importar el módulo
load_dotenv()

class AdaptariaAPI:

    def __init__(self):
        self.base_url = os.getenv("ADAPTARIA_URL")
        self.jwt_token = None
        self._authenticated = False

    def auth(self):
        """
        Autentica con Adaptaria y guarda el JWT token
        Returns:
            str: JWT token si la autenticación es exitosa
        Raises:
            APIRequestError: Si falla la autenticación
        """
        try:
            connector_logger.info("Authenticating with Adaptaria API")
            
            email = os.getenv("ADAPTARIA_EMAIL")
            password = os.getenv("ADAPTARIA_PASSWORD")
            
            if not email or not password:
                raise APIRequestError("Adaptaria credentials not found in environment variables")
            
            payload = {
                "email": email,
                "password": password
            }
            
            response = requests.post(self.base_url + '/auth/', json=payload)
            
            if not response.ok:
                connector_logger.error(f"Authentication failed with status {response.status_code}")
                response.raise_for_status()
            
            jwt_token = response.cookies.get("access_token")
            
            if not jwt_token:
                raise APIRequestError("access_token not found in response cookies")
            
            self.jwt_token = jwt_token
            self._authenticated = True
            
            connector_logger.info("Successfully authenticated with Adaptaria API")
            return jwt_token
            
        except requests.exceptions.RequestException as e:
            connector_logger.error(f"Request error during authentication: {str(e)}", exc_info=True)
            raise APIRequestError(f"Failed to authenticate with Adaptaria: {str(e)}")
        except Exception as e:
            connector_logger.error(f"Unexpected error during authentication: {str(e)}", exc_info=True)
            raise APIRequestError(f"Authentication error: {str(e)}")

    def _ensure_authenticated(self):
        """Asegura que el API esté autenticada antes de hacer peticiones"""
        if not self._authenticated or not self.jwt_token:
            connector_logger.debug("Not authenticated, attempting to authenticate")
            self.auth()
 
    def request(self, endpoint: Constant, method: str, payload={}, url_params={}, files=None, **kwargs) -> dict:
        # Asegurar autenticación antes de cada petición
        self._ensure_authenticated()
        endpoint = self.base_url + endpoint.value
        id_in_url = ":id" in endpoint
        if url_params:
            endpoint = self.fill_url(endpoint, url_params)

        # Usar el access_token obtenido durante la autenticación
        cookies = {"access_token": self.jwt_token}
        method = method.lower()
        if method == 'post':
            connector_logger.info(f"[AdaptariaAPI] POST {endpoint} | Payload: {payload} | Files: {files} | Cookies: {cookies}")
            # Si hay archivos, usar data= en lugar de json= para multipart/form-data
            if files:
                response = requests.post(endpoint, data=payload, cookies=cookies, files=files, **kwargs)
            else:
                response = requests.post(endpoint, json=payload, cookies=cookies, **kwargs)
        elif method == 'get':
            if "id" in url_params and not id_in_url:
                endpoint += f"/{url_params['id']}"
            elif "id" in payload and not id_in_url:
                endpoint += f"/{payload['id']}"
            # INSERT_YOUR_CODE
            response = requests.get(endpoint, cookies=cookies, **kwargs)

        elif method == 'put':
            response = requests.put(endpoint, json=payload, cookies=cookies, **kwargs)
        elif method == 'delete':
            response = requests.delete(endpoint, json=payload, cookies=cookies, **kwargs)
        elif method == 'patch':
            if "id" in url_params:
                endpoint += f"/{url_params['id']}"
            elif "id" in payload:
                endpoint += f"/{payload['id']}"
            response = requests.patch(endpoint, json=payload, cookies=cookies, **kwargs)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
            
        print(f"[AdaptarIA] {method.upper()} {endpoint} - Response: {response.status_code}")
        
        # Manejar respuestas sin contenido o sin JSON
        if response.status_code == 204 or not response.content:
            return {}
        
        try:
            return response.json().get("data", {})
        except requests.exceptions.JSONDecodeError:
            # Si la respuesta no es JSON, retornar objeto vacío
            return {}

    def fill_url(self, url, params):
        return re.sub(r":(\w+)", lambda m: str(params.get(m.group(1), m.group(0))), url)

class AdaptariaEndpoints(Enum):
    INSTITUTES = "/institutes"
    COURSES = "/courses"
    USERS = "/users"
    STUDENTS = "/students"
    DIRECTOR = "/directors"
    ENROLLED_COURSES = "/students/me/courses"

class AdaptariaCourseEndpoints(Enum):
    CREATE = '/connector' + AdaptariaEndpoints.COURSES.value
    UPDATE = '/connector' + AdaptariaEndpoints.COURSES.value
    GET = '/connector' + AdaptariaEndpoints.COURSES.value
    ADD_STUDENT = '/connector' + AdaptariaEndpoints.COURSES.value + "/:courseId/students"
    GET_SECTIONS = '/connector' + AdaptariaEndpoints.COURSES.value + "/:id/sections"
    GET_STUDENTS = '/connector' + AdaptariaEndpoints.COURSES.value + "/:id/students"

class AdaptariaUserEndpoints(Enum):
    GET = '/connector' + AdaptariaEndpoints.USERS.value
    GET_BY_EMAIL = '/connector' + AdaptariaEndpoints.USERS.value + '/get_by_email'
    GET_HASHED_PASSWORD = '/connector' + AdaptariaEndpoints.USERS.value + '/get_hashed_password'
    UPDATE = '/connector' + AdaptariaEndpoints.USERS.value + "/me"
    UPDATE_ROLE = '/connector' + AdaptariaEndpoints.USERS.value + "/:userId/role"

class AdaptariaStudentEndponints(Enum):
    CREATE = '/connector' + AdaptariaEndpoints.STUDENTS.value
    UPDATE = '/connector' + AdaptariaEndpoints.STUDENTS.value
    GET = AdaptariaEndpoints.STUDENTS.value

class AdaptariaDirectorEndponints(Enum):
    CREATE = '/connector' + AdaptariaEndpoints.DIRECTOR.value

class AdaptariaSectionEndpoints(Enum):
    CREATE = '/connector' + AdaptariaEndpoints.COURSES.value + '/:courseId/sections'
    UPDATE = '/connector' + AdaptariaEndpoints.COURSES.value + '/:courseId/sections/:sectionId'
    GET =  '/connector' + AdaptariaEndpoints.COURSES.value + "/:courseId/sections/:sectionId"
    GET_CONTENTS = '/connector/sections/:id/contents'

class AdaptariaContentEndpoints(Enum):
    CREATE = "/connector/courses/contents/:sectionId"
    GET =  '/connector/contents'

class AdaptariaInstituteEndpoints(Enum):
    CREATE = '/connector' + AdaptariaEndpoints.INSTITUTES.value
    UPDATE = '/connector' + AdaptariaEndpoints.INSTITUTES.value + '/:id'
    GET = '/connector' + AdaptariaEndpoints.INSTITUTES.value + '/:id'
    GET_COURSES = '/connector' + AdaptariaEndpoints.INSTITUTES.value + '/:id/courses'
    GET_DIRECTORS = '/connector' + AdaptariaEndpoints.INSTITUTES.value + '/:id/directors'
    GET_STUDENTS = '/connector' + AdaptariaEndpoints.INSTITUTES.value + '/:id/students'
    GET_TEACHERS = '/connector' + AdaptariaEndpoints.INSTITUTES.value + '/:id/teachers'
