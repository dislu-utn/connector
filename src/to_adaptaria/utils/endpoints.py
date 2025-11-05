from ast import Constant
from enum import Enum
import re


import requests

class AdaptariaAPI:

    def __init__(self):
        self.base_url = "adaptaria.com"

    def request(self, endpoint: Constant, method: str, payload=None, url_params=None, files=None, **kwargs) -> dict:
        endpoint = self.base_url + endpoint.value
        if url_params:
            endpoint = self.fill_url(endpoint, url_params)

        cookies = {"id": "123"}
        method = method.lower()
        if method == 'post':
            response = requests.post(endpoint, json=payload, cookies=cookies, files=files, **kwargs)
        elif method == 'get':
            if "id" in url_params:
                endpoint += f"/{url_params["id"]}"
            elif "id" in payload:
                endpoint += f"/{payload["id"]}"
            response = requests.get(endpoint, cookies=cookies, **kwargs)
        elif method == 'put':
            response = requests.put(endpoint, json=payload, cookies=cookies, **kwargs)
        elif method == 'delete':
            response = requests.delete(endpoint, json=payload, cookies=cookies, **kwargs)
        elif method == 'patch':
            if "id" in url_params:
                endpoint += f"/{url_params["id"]}"
            elif "id" in payload:
                endpoint += f"/{payload["id"]}"
            response = requests.patch(endpoint, params=payload, cookies=cookies, **kwargs)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        print(f"[AdaptarIA] {method.upper()} {endpoint} - Response: {response.status_code}")
        return response.json()

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
    ADD_STUDENT = '/connector' + AdaptariaEndpoints.COURSES.value + "/:courseId/students"

class AdaptariaUserEndpoints(Enum):
    GET = '/connector' + AdaptariaEndpoints.USERS.value
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
    CREATE = '/connector' + 'AdaptariaEndpoints.COURSES.value' + '/:courseId/sections'
    UPDATE = '/connector' + 'AdaptariaEndpoints.COURSES.value' + '/:courseId/sections/:sectionId'
    GET =  '/connector' + AdaptariaEndpoints.COURSES.value + "/:courseId/sections/:sectionId"

class AdaptariaContentEndpoints(Enum):
    CREATE = "/connector/contents/:sectionId"
    GET =  '/connector/contents'

class AdaptariaInstituteEndpoints(Enum):
    CREATE = '/connector' + AdaptariaEndpoints.INSTITUTES.value
    UPDATE = '/connector' + AdaptariaEndpoints.INSTITUTES.value + '/:id'
    GET = '/connector' + AdaptariaEndpoints.INSTITUTES.value + '/:id'
