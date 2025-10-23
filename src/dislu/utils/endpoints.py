from enum import Enum

class DisluEndpoints(Enum):
    INSTITUTIONS = "/institution/"
    USERS = "/users/"
    USER_X_COURSE = ""
    COURSES = "/courses/"
    ROADMAPS = "/roadmaps/"
    STUDY_MATERIALS = ""

class InstitutionEndpoints(Enum):
    CREATE = DisluEndpoints.INSTITUTIONS.value + "create"
