from enum import Enum

class AdaptariaEndpoints(Enum):
    INSTITUTES = "/institutes/"


class InstituteEndpoints(Enum):
    CREATE = AdaptariaEndpoints.INSTITUTES.value
