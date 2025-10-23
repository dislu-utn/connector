from src.dislu.utils.endpoints import DisluEndpoints, InstitutionEndpoints
from src.shared.integrate_dto  import IntegrateDTO
from src.adaptaria.utils.endpoints import InstituteEndpoints
from src.adaptaria.transformer.models import AdaptariaCreateInstitutePayload
from src.dislu.transformer.models import DisluCreateInstitutionPayload
from src.shared.transformer import TransformedRequest
from test.shared.base_test import BaseTest

dislu_create_institution_payload: DisluCreateInstitutionPayload = {
    "name": "TestName",
    "domain": "TestDomain"
}

adaptaria_create_institution_paylaod: AdaptariaCreateInstitutePayload = {
    "name": "TestName",
    "address": "TestAddress",
    "phone": "TestPhone"
}

class InstitutionTest(BaseTest):

    def test_create_from_dislu_to_adaptaria(self):
        """Test transformation from Dislu to Adaptaria format."""
        message = IntegrateDTO(
            institution_id="test_id", 
            origin="dislu", 
            payload=dislu_create_institution_payload, 
            endpoint= InstitutionEndpoints.CREATE.value,
            method="post"
        )
        
        self.initialize(message.origin)
        self.connector.provider.initialize(message)
        transformed_request = self.connector.provider.transform()
        
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

    def test_create_from_adaptaria_to_dislu(self):
        """Test transformation from Adaptaria to Dislu format."""
        message = IntegrateDTO(
            institution_id="test_id", 
            origin="adaptaria", 
            payload=adaptaria_create_institution_paylaod, 
            endpoint= InstituteEndpoints.CREATE.value,
            method="post"
        )
        
        self.initialize(message.origin)
        self.connector.provider.initialize(message)
        transformed_request = self.connector.provider.transform()
        
        # Expected result structure
        expected_body = {
            "name": "TestName",
            "domain": ""
        }

        # Assert the transformation result
        self.assertIsInstance(transformed_request, TransformedRequest)
        self.assertEqual(transformed_request.payload, expected_body)
        self.assertEqual(transformed_request.url, InstitutionEndpoints.CREATE.value)
        self.assertEqual(transformed_request.method, "post")

def run():
    import unittest
    unittest.main()


