from ast import List
import requests
from src.to_dislu.utils.endpoints import InstitutionEndpoints
from src.shared.transformer import TransformedRequest, Transformer
from src.to_adaptaria.utils.endpoints import AdaptariaEndpoints, AdaptariaInstituteEndpoints
from src.shared.logger import connector_logger, APIRequestError, ValidationError

class DisluInstitutionTransformer(Transformer):

    def run(self, entity:str, entity_id: str, method:str):
        try:
            connector_logger.info(f"Starting DisluInstitutionTransformer - Entity: {entity}, ID: {entity_id}, Method: {method}")
            
            if "create" in method:
                result = self.create(entity, entity_id)
                connector_logger.info(f"Successfully created institution in Dislu - Entity: {entity}, ID: {entity_id}")
                return result
            if "update" in method:
                result = self.update(entity, entity_id)
                connector_logger.info(f"Successfully updated institution in Dislu - Entity: {entity}, ID: {entity_id}")
                return result

            connector_logger.warning(f"No handler found for method: {method}")
            return None
            
        except Exception as e:
            connector_logger.error(f"Error in DisluInstitutionTransformer - Entity: {entity}, ID: {entity_id}, Method: {method} | Error: {str(e)}", exc_info=True)
            raise

    def create(self, entity: str, entity_id:str):
        try:
            connector_logger.info(f"Creating institution in Dislu from Adaptaria institute - ID: {entity_id}")
            
            # Obtener instituto de Adaptaria
            adaptaria_institute = self.adaptaria_api.request(
                AdaptariaInstituteEndpoints.GET, 
                "get", 
                None, 
                {"id": entity_id}
            )
            if not adaptaria_institute:
                raise ValidationError("Institute not found in Adaptaria", entity=entity, entity_id=entity_id)
            
            connector_logger.debug(f"Retrieved Adaptaria institute: {adaptaria_institute.get('name')}")

            # Validar campos requeridos
            if not adaptaria_institute.get("name"):
                raise ValidationError("Institute name is required", entity=entity, entity_id=entity_id)

            payload = {
                "name": adaptaria_institute.get("name"),
                "domain": "",  # Mapear address a domain si es necesario
                "external_reference": entity_id
            }

            connector_logger.info(f"Creating institution in Dislu: {payload['name']}")
            response = self.dislu_api.request(
                InstitutionEndpoints.CREATE,
                "post",
                payload
            )
            
            if not response or not response.get("id"):
                raise APIRequestError("Failed to create institution in Dislu - no ID returned", entity=entity, entity_id=entity_id)
            
            connector_logger.info(f"Institution created successfully in Dislu - ID: {response.get('id')}")
            return response
            
        except (ValidationError, APIRequestError) as e:
            connector_logger.error(f"Validation/API error creating institution: {str(e)}")
            raise
        except Exception as e:
            connector_logger.error(f"Unexpected error creating institution in Dislu - ID: {entity_id} | Error: {str(e)}", exc_info=True)
            raise APIRequestError(f"Failed to create institution: {str(e)}", entity=entity, entity_id=entity_id)

    def update(self, entity: str, entity_id:str):
        try:
            connector_logger.info(f"Updating institution in Dislu from Adaptaria institute - ID: {entity_id}")
            
            # Obtener instituto de Adaptaria
            adaptaria_institute = self.adaptaria_api.request(
                AdaptariaInstituteEndpoints.GET,
                "get",
                None,
                {"id": entity_id}
            )
            if not adaptaria_institute:
                raise ValidationError("Institute not found in Adaptaria", entity=entity, entity_id=entity_id)
            
            # Obtener institución de Dislu por referencia externa
            dislu_institution = self.dislu_api.request(
                InstitutionEndpoints.GET_EXTERNAL,
                "get",
                None,
                {"id": entity_id}
            )
            if not dislu_institution:
                raise ValidationError("Institution not found in Dislu with external reference", entity=entity, entity_id=entity_id)

            connector_logger.debug(f"Comparing institutions - Adaptaria: {adaptaria_institute.get('name')}, Dislu: {dislu_institution.get('name')}")

            payload = {}

            # Comparar campos
            if adaptaria_institute.get("name") != dislu_institution.get("name"):
                payload["name"] = adaptaria_institute.get("name")
                connector_logger.debug(f"Name needs update: {adaptaria_institute.get('name')}")

            if not payload:
                connector_logger.info(f"No institution fields need updating for {entity_id}")
                return None

            payload["id"] = dislu_institution.get("id")

            connector_logger.info(f"Updating institution fields in Dislu: {list(payload.keys())}")
            response = self.dislu_api.request(InstitutionEndpoints.UPDATE, "post", payload)
            connector_logger.info(f"Institution updated successfully in Dislu")
            return response
            
        except (ValidationError, APIRequestError) as e:
            connector_logger.error(f"Validation/API error updating institution: {str(e)}")
            raise
        except Exception as e:
            connector_logger.error(f"Unexpected error updating institution in Dislu - ID: {entity_id} | Error: {str(e)}", exc_info=True)
            raise APIRequestError(f"Failed to update institution: {str(e)}", entity=entity, entity_id=entity_id)

