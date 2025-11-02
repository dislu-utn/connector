from ast import Constant
from enum import Enum
from http.client import HTTPResponse

import requests
import re

from urllib3.util import url

class DisluAPI:

    def __init__(self):
        self.base_url = "http://localhost:4000/api"

    def request(self, endpoint: Constant, method: str, payload=None, url_params=None, **kwargs) -> dict:
        endpoint = self.base_url + endpoint.value
        if url_params:
            endpoint = self.fill_url(endpoint, url_params)

        cookies = {"token": "123"}
        method = method.lower()
        if method == 'post':
            response = requests.post(endpoint, json=payload, cookies=cookies, **kwargs)
        elif method == 'get':
            response = requests.get(endpoint, cookies=cookies, **kwargs)
        elif method == 'put':
            response = requests.put(endpoint, json=payload, cookies=cookies, **kwargs)
        elif method == 'delete':
            response = requests.delete(endpoint, json=payload, cookies=cookies, **kwargs)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        print(f"[DisluAPI] {method.upper()} {endpoint} - Response: {response.status_code}")
        print("Status Code:", response.url)
        return response.json()

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
    CREATE = DisluEndpoints.INSTITUTIONS.value + "/create"
    UPDATE = DisluEndpoints.INSTITUTIONS.value + "/update"
    GET = DisluEndpoints.INSTITUTIONS.value #TODO
    GET_EXTERNAL = DisluEndpoints.INSTITUTIONS.value + "/get_external/:id" #Done

    

class CourseEndpoints(Enum):
    CREATE = DisluEndpoints.COURSES.value + "/create"
    UPDATE = DisluEndpoints.COURSES.value + "/update"
    GET = DisluEndpoints.COURSES.value + "/:id"
    GET_EXTERNAL = DisluEndpoints.COURSES.value + "/get_external/:id" #Done


class UsersEndpoints(Enum):
    CREATE = DisluEndpoints.USERS.value + "/create"
    UPDATE = DisluEndpoints.USERS.value + "/update"
    GET = DisluEndpoints.USERS.value + "/:id"
    GET_EXTERNAL = DisluEndpoints.USERS.value + "/get_external/:id" #Done
    ENROLL = DisluEndpoints.USERS.value + "/enroll" #Lo recibe la entity user_x_course
    ASSIGN_PROFESSOR = DisluEndpoints.USERS.value + "/assign_professor" #Lo recibe la entity user_x_course

class UsersXCourseEndpoints(Enum):
    GET_PROFESSOR_BY_EXTERNAL_ID = DisluEndpoints.USER_X_COURSE.value + "/get_professor_by_external_id"
    ENROLLED_COURSES = DisluEndpoints.USER_X_COURSE.value + "/courses"
