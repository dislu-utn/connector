# Sistema de Logging y Manejo de Errores del Connector

## Resumen

Se ha implementado un sistema completo de logging y manejo de errores en todos los transformers del connector para facilitar el debugging, monitoreo y resolución de problemas en la sincronización entre Dislu y Adaptaria.

## Componentes Principales

### 1. Logger Configurado (`src/shared/logger.py`)

El módulo de logging proporciona:

- **Logger global**: `connector_logger` disponible en todos los transformers
- **Formato detallado**: Incluye timestamp, nivel, nombre del módulo, función, línea y mensaje
- **Salidas duales**:
  - Consola (stdout) para monitoreo en tiempo real
  - Archivo `connector.log` para análisis posterior
- **Niveles de logging**: INFO, DEBUG, WARNING, ERROR, CRITICAL

### 2. Excepciones Personalizadas

#### `TransformerError` (Base)
Excepción base que incluye:
- `message`: Descripción del error
- `entity`: Tipo de entidad afectada
- `entity_id`: ID de la entidad
- `details`: Diccionario con información adicional

#### `APIRequestError`
Para errores en peticiones a APIs externas (Dislu o Adaptaria)

#### `ValidationError`
Para errores de validación de datos

#### `MappingError`
Para errores en el mapeo de campos entre sistemas

## Niveles de Logging

### INFO
Usado para:
- Inicio y fin de operaciones principales
- Acciones exitosas
- Flujo normal del programa

```python
connector_logger.info(f"Creating user in Adaptaria - Entity: {entity}, ID: {entity_id}")
connector_logger.info(f"User created successfully in Adaptaria")
```

### DEBUG
Usado para:
- Detalles de datos recuperados
- Comparaciones de campos
- Información técnica detallada

```python
connector_logger.debug(f"Retrieved Dislu user: {dislu_user.get('email')}")
connector_logger.debug(f"Profile picture needs update")
```

### WARNING
Usado para:
- Situaciones anómalas que no impiden el funcionamiento
- Métodos no implementados
- Recursos no encontrados (cuando es esperado)

```python
connector_logger.warning(f"No handler found for method: {method}")
connector_logger.warning(f"Roadmap has no external reference in Adaptaria")
```

### ERROR
Usado para:
- Errores capturados y manejados
- Fallos de validación
- Errores de API
- Excepciones inesperadas

```python
connector_logger.error(f"Validation/API error creating user: {str(e)}")
connector_logger.error(f"Unexpected error creating user in Adaptaria | Error: {str(e)}", exc_info=True)
```

## Estructura de Manejo de Errores

Todos los transformers siguen este patrón:

```python
def run(self, entity:str, entity_id: str, method:str):
    try:
        connector_logger.info(f"Starting [Transformer] - Entity: {entity}, ID: {entity_id}, Method: {method}")
        
        if "create" in method:
            result = self.create(entity, entity_id)
            connector_logger.info(f"Successfully created [entity] - Entity: {entity}, ID: {entity_id}")
            return result
        # ... más métodos
        
        connector_logger.warning(f"No handler found for method: {method}")
        return None
        
    except Exception as e:
        connector_logger.error(f"Error in [Transformer] - Entity: {entity}, ID: {entity_id}, Method: {method} | Error: {str(e)}", exc_info=True)
        raise
```

### Métodos individuales

```python
def create(self, entity: str, entity_id:str):
    try:
        connector_logger.info(f"Creating [entity] ...")
        
        # 1. Validar datos de entrada
        if not data:
            raise ValidationError("Data not found", entity=entity, entity_id=entity_id)
        
        # 2. Validar campos requeridos
        if not data.get("required_field"):
            raise ValidationError("Required field is missing", entity=entity, entity_id=entity_id)
        
        # 3. Realizar operación
        response = self.api.request(...)
        
        # 4. Validar respuesta
        if not response or not response.get("id"):
            raise APIRequestError("Failed to create", entity=entity, entity_id=entity_id)
        
        connector_logger.info(f"[Entity] created successfully")
        return response
        
    except (ValidationError, APIRequestError) as e:
        connector_logger.error(f"Validation/API error: {str(e)}")
        raise
    except Exception as e:
        connector_logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise APIRequestError(f"Failed to create: {str(e)}", entity=entity, entity_id=entity_id)
```

## Validaciones Implementadas

### 1. Validación de Existencia
```python
dislu_user = self.dislu_api.request(UsersEndpoints.GET, "get", None, {"id": entity_id})
if not dislu_user:
    raise ValidationError("User not found in Dislu", entity=entity, entity_id=entity_id)
```

### 2. Validación de Campos Requeridos
```python
if not dislu_user.get("name"):
    raise ValidationError("User name is required", entity=entity, entity_id=entity_id)
```

### 3. Validación de Referencias Externas
```python
if not dislu_user.get("external_reference"):
    raise ValidationError("User has no external reference in Adaptaria", entity=entity, entity_id=entity_id)
```

### 4. Validación de Formato de IDs
```python
if "/" not in entity_id:
    raise ValidationError("Invalid entity_id format, expected 'user_id/course_id'", entity=entity, entity_id=entity_id)
```

### 5. Validación de Respuestas
```python
if not response or not response.get("id"):
    raise APIRequestError("Failed to create user in Adaptaria - no ID returned", entity=entity, entity_id=entity_id)
```

## Transformers Actualizados

### To Adaptaria
- ✅ `AdaptariaUsersTransformer`
- ✅ `AdaptariaCoursesTransformer`
- ✅ `AdaptariaSubjectTransformer`
- ✅ `AdaptariaContentsTransformer`

### To Dislu
- ✅ `DisluUsersTransformer`
- ✅ `DisluCoursesTransformer`
- ✅ `DisluRoadmapTransformer`
- ✅ `DisluStudyMaterialTransformer`

## Uso del Logger

### Importar el logger
```python
from src.shared.logger import connector_logger, APIRequestError, ValidationError
```

### Ejemplos de uso

```python
# Información general
connector_logger.info(f"Starting synchronization for user {user_id}")

# Debug detallado
connector_logger.debug(f"Comparing fields: {field1} vs {field2}")

# Advertencias
connector_logger.warning(f"External reference not found for entity {entity_id}")

# Errores
connector_logger.error(f"Failed to sync user {user_id}: {str(e)}", exc_info=True)
```

## Archivo de Log

El archivo `connector.log` contiene:
- Todos los eventos con nivel INFO o superior
- Stack traces completos de excepciones
- Timestamp de cada operación
- Contexto completo de cada error

### Formato de log
```
2024-01-15 10:30:45 | INFO     | connector.to_adaptaria.users_transformers | create:31 | Creating user in Adaptaria - Entity: student, ID: 12345
2024-01-15 10:30:46 | DEBUG    | connector.to_adaptaria.users_transformers | create:38 | Retrieved Dislu user: student@example.com
2024-01-15 10:30:47 | INFO     | connector.to_adaptaria.users_transformers | create:83 | User created successfully in Adaptaria - Adaptaria ID: 67890
```

## Beneficios

1. **Debugging más fácil**: Logs detallados permiten rastrear el flujo completo de cada operación
2. **Detección temprana de errores**: Validaciones exhaustivas previenen errores en cascada
3. **Mensajes de error claros**: Cada error indica exactamente qué falló y dónde
4. **Trazabilidad**: Cada operación queda registrada con timestamp y contexto
5. **Monitoreo**: Los logs permiten monitorear el health del connector en producción
6. **Análisis post-mortem**: Los logs facilitan el análisis de incidentes pasados

## Configuración del Nivel de Logging

Para cambiar el nivel de logging (ej. para más detalle en desarrollo):

```python
from src.shared.logger import setup_logger
import logging

# Para modo desarrollo con más detalle
logger = setup_logger("connector", level=logging.DEBUG)

# Para producción con menos ruido
logger = setup_logger("connector", level=logging.INFO)
```

## Recomendaciones

1. **Revisar logs regularmente**: Especialmente los WARNING para detectar problemas potenciales
2. **Monitorear el archivo de log**: Implementar alertas para errores críticos
3. **Rotar logs**: Implementar rotación de logs para evitar archivos muy grandes
4. **No logear información sensible**: Evitar logear passwords, tokens, etc.
5. **Usar niveles apropiados**: INFO para operaciones normales, DEBUG solo para debugging

## Próximos Pasos

1. Implementar rotación de logs (RotatingFileHandler)
2. Agregar logging a archivos separados por tipo de transformer
3. Implementar métricas y alertas basadas en logs
4. Integrar con sistemas de monitoreo (ej. Sentry, CloudWatch)

