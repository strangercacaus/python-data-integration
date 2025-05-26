from typing import Dict, Type
from .base import DataType, TypeDefinition

class TypeRegistry:
    def __init__(self):
        self._mappings: Dict[str, Dict[DataType, TypeDefinition]] = {}
    
    def register_connector(self, connector_name: str, mappings: Dict[DataType, TypeDefinition]):
        self._mappings[connector_name] = mappings
    
    def get_type_definition(self, connector_name: str, data_type: DataType) -> TypeDefinition:
        return self._mappings.get(connector_name, {}).get(data_type)