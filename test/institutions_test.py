from src.dislu.utils.endpoints import DisluEndpoints, InstitutionEndpoints
from src.shared.integrate_dto  import IntegrateDTO
from src.adaptaria.utils.endpoints import InstituteEndpoints
from src.dislu.transformer.models.intitution_models import AdaptariaCreateInstitutionPayload, DisluCreateInstitutionPayload
from src.shared.transformer import TransformedRequest
from test.shared.base_test import BaseTest

dislu_create_institution_payload: DisluCreateInstitutionPayload = {
    "name": "TestName",
    "domain": "TestDomain"
}

adaptaria_create_institution_paylaod: AdaptariaCreateInstitutionPayload = {
    "name": "TestName",
    "address": "TestAddress",
    "phone": "TestPhone"
}

class InstitutionTest(BaseTest):

    def test_create_from_dislu_to_adaptaria(self):
        """Test transformation from Dislu to Adaptaria format."""
        self.initialize("dislu")
        message = IntegrateDTO(
            institution_id="test_id", 
            origin="dislu", 
            payload=dislu_create_institution_payload, 
            endpoint= InstitutionEndpoints.CREATE.value,
            method="post"
        )
        transformed_request = self.connector.transform(message)
        
        # Expected result structure
        expected_body = {
            "name": "TestName",
            "address": "",
            "phone": ""
        }

        # Assert the transformation result
        self.assertIsInstance(transformed_request, TransformedRequest)
        self.assertEqual(transformed_request.payload, expected_body)
        self.assertEqual(transformed_request.url, InstituteEndpoints.CREATE.value)
        self.assertEqual(transformed_request.method, "post")

def run():
    import unittest
    unittest.main()


