import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.shared.integrate_dto import IntegrateDTO
from src.to_dislu.utils.endpoints import CourseEndpoints, DisluAPI, InstitutionEndpoints


def create_dislu_course():
    dislu_api = DisluAPI()
    external_institution_reference = "00000000-0000-4000-8000-000000000000" 
    dislu_institution = dislu_api.request(InstitutionEndpoints.GET_EXTERNAL, "get", {"id": external_institution_reference})

    
    payload = {
        "institution": dislu_institution.get("id"),
        "name": "Test Connector",
        "description": "Test Connector",
        "matriculation_key": "Test Connector",
        "external_reference": external_institution_reference
    }
    
    return dislu_api.request(CourseEndpoints.CREATE, "post", payload)

print(create_dislu_course())
    
