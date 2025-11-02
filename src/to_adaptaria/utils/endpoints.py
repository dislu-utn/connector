from ast import Constant
from enum import Enum
import re


import requests

class AdaptariaAPI:

    def __init__(self):
        self.base_url = "adaptaria.com"

    def request(self, endpoint: Constant, method: str, payload=None, url_params=None, **kwargs) -> dict:
        endpoint = self.base_url + endpoint.value
        if url_params:
            endpoint = self.fill_url(endpoint, url_params)

        cookies = {"id": "123"}
        method = method.lower()
        if method == 'post':
            response = requests.post(endpoint, json=payload, cookies=cookies, **kwargs)
        elif method == 'get':
            if "id" in payload:
                endpoint += f"/{payload["id"]}"
            response = requests.get(endpoint, cookies=cookies, **kwargs)
        elif method == 'put':
            response = requests.put(endpoint, json=payload, cookies=cookies, **kwargs)
        elif method == 'delete':
            response = requests.delete(endpoint, json=payload, cookies=cookies, **kwargs)
        elif method == 'patch':
            response = requests.patch(endpoint, json=payload, cookies=cookies, **kwargs)
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
    ENROLLED_COURSES = "/students/me/courses"
    ADD_STUDENT_TO_COURSE = "/courses/:courseId/students"
    UPDATE_USER_ROLE = "/users/:userId/role"
