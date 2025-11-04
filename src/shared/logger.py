import logging
import sys
from datetime import datetime
from typing import Optional

# Configurar el logger
def setup_logger(name: str = "connector", level: int = logging.INFO) -> logging.Logger:
    """
    Configura y retorna un logger para el connector
    
    Args:
        name: Nombre del logger
        level: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        Logger configurado
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Evitar duplicar handlers si ya existe
    if logger.handlers:
        return logger
    
    # Formato detallado para logs
    formatter = logging.Formatter(
        fmt='%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler para consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Handler para archivo
    file_handler = logging.FileHandler('connector.log', encoding='utf-8')
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger

# Logger global para el connector
connector_logger = setup_logger()

class TransformerError(Exception):
    """Excepción base para errores en transformers"""
    def __init__(self, message: str, entity: Optional[str] = None, entity_id: Optional[str] = None, details: Optional[dict] = None):
        self.message = message
        self.entity = entity
        self.entity_id = entity_id
        self.details = details or {}
        super().__init__(self.message)
    
    def __str__(self):
        error_msg = f"{self.message}"
        if self.entity:
            error_msg += f" | Entity: {self.entity}"
        if self.entity_id:
            error_msg += f" | ID: {self.entity_id}"
        if self.details:
            error_msg += f" | Details: {self.details}"
        return error_msg

class APIRequestError(TransformerError):
    """Error en request a API externa"""
    pass

class MappingError(TransformerError):
    """Error en mapeo de campos"""
    pass

class ValidationError(TransformerError):
    """Error de validación de datos"""
    pass

