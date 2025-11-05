import requests
from src.to_dislu.utils.endpoints import InstitutionEndpoints
from src.shared.transformer import TransformedRequest, Transformer
from src.to_adaptaria.utils.endpoints import AdaptariaInstituteEndpoints
from src.shared.logger import connector_logger, APIRequestError, ValidationError

class AdaptariaInstituteTransformer(Transformer):

    def run(self, entity:str, entity_id: str, method:str):
        try:
            connector_logger.info(f"Starting AdaptariaInstituteTransformer - Entity: {entity}, ID: {entity_id}, Method: {method}")
            
            if "create" in method:
                result = self.create(entity, entity_id)
                connector_logger.info(f"Successfully created institute in Adaptaria - Entity: {entity}, ID: {entity_id}")
                return result
            if "update" in method:
                result = self.update(entity, entity_id)
                connector_logger.info(f"Successfully updated institute in Adaptaria - Entity: {entity}, ID: {entity_id}")
                return result

            connector_logger.warning(f"No handler found for method: {method}")
            return None
            
        except Exception as e:
            connector_logger.error(f"Error in AdaptariaInstituteTransformer - Entity: {entity}, ID: {entity_id}, Method: {method} | Error: {str(e)}", exc_info=True)
            raise

    def create(self, entity: str, entity_id:str):
        try:
            connector_logger.info(f"Creating institute in Adaptaria from Dislu institution - ID: {entity_id}")
            
            # Obtener institución de Dislu
            dislu_institution = self.dislu_api.request(
                InstitutionEndpoints.GET,
                "get",
                None,
                {"id": entity_id}
            )
            if not dislu_institution:
                raise ValidationError("Institution not found in Dislu", entity=entity, entity_id=entity_id)
            
            connector_logger.debug(f"Retrieved Dislu institution: {dislu_institution.get('name')}")

            # Validar campos requeridos
            if not dislu_institution.get("name"):
                raise ValidationError("Institution name is required", entity=entity, entity_id=entity_id)

            payload = {
                "name": dislu_institution.get("name"),
                "address": "",  # Mapear domain a address
                "phone": ""  # Campo requerido en Adaptaria pero no existe en Dislu
            }

            connector_logger.info(f"Creating institute in Adaptaria: {payload['name']}")
            response = self.adaptaria_api.request(
                AdaptariaInstituteEndpoints.CREATE,
                "post",
                payload
            )
            
            if not response or not response.get("id"):
                raise APIRequestError("Failed to create institute in Adaptaria - no ID returned", entity=entity, entity_id=entity_id)
            
            connector_logger.info(f"Institute created successfully in Adaptaria - ID: {response.get('id')}")

            # Actualizar referencia externa en Dislu
            self.dislu_api.update_external_reference(
                InstitutionEndpoints.UPDATE,
                dislu_institution.get("id"),
                response.get("id")
            )
            
            connector_logger.info(f"External reference updated in Dislu for institution {entity_id}")
            return response
            
        except (ValidationError, APIRequestError) as e:
            connector_logger.error(f"Validation/API error creating institute: {str(e)}")
            raise
        except Exception as e:
            connector_logger.error(f"Unexpected error creating institute in Adaptaria - ID: {entity_id} | Error: {str(e)}", exc_info=True)
            raise APIRequestError(f"Failed to create institute: {str(e)}", entity=entity, entity_id=entity_id)

    def update(self, entity: str, entity_id:str):
        try:
            connector_logger.info(f"Updating institute in Adaptaria from Dislu institution - ID: {entity_id}")
            
            # Obtener institución de Dislu
            dislu_institution = self.dislu_api.request(
                InstitutionEndpoints.GET,
                "get",
                None,
                {"id": entity_id}
            )
            if not dislu_institution:
                raise ValidationError("Institution not found in Dislu", entity=entity, entity_id=entity_id)
            
            # Validar que tenga referencia externa
            if not dislu_institution.get("external_reference"):
                raise ValidationError("Institution has no external reference in Adaptaria", entity=entity, entity_id=entity_id)
            
            # Obtener instituto de Adaptaria
            adaptaria_institute = self.adaptaria_api.request(
                AdaptariaInstituteEndpoints.GET,
                "get",
                None,
                {"id": dislu_institution.get("external_reference")}
            )
            if not adaptaria_institute:
                raise ValidationError("Institute not found in Adaptaria", entity=entity, entity_id=dislu_institution.get("external_reference"))

            connector_logger.debug(f"Comparing institutes - Dislu: {dislu_institution.get('name')}, Adaptaria: {adaptaria_institute.get('name')}")

            payload = {}

            # Comparar campos
            if dislu_institution.get("name") != adaptaria_institute.get("name"):
                payload["name"] = dislu_institution.get("name")
                connector_logger.debug(f"Name needs update: {dislu_institution.get('name')}")

            if not payload:
                connector_logger.info(f"No institute fields need updating for {entity_id}")
                return None

            connector_logger.info(f"Updating institute fields in Adaptaria: {list(payload.keys())}")
            response = self.adaptaria_api.request(
                AdaptariaInstituteEndpoints.UPDATE,
                "patch",
                payload,
                {"id": adaptaria_institute.get("id")}
            )
            connector_logger.info(f"Institute updated successfully in Adaptaria")
            return response
            
        except (ValidationError, APIRequestError) as e:
            connector_logger.error(f"Validation/API error updating institute: {str(e)}")
            raise
        except Exception as e:
            connector_logger.error(f"Unexpected error updating institute in Adaptaria - ID: {entity_id} | Error: {str(e)}", exc_info=True)
            raise APIRequestError(f"Failed to update institute: {str(e)}", entity=entity, entity_id=entity_id)

