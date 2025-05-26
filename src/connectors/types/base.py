from enum import Enum
from typing import Any

class DataType(Enum):
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    # ... other types ...

class TypeDefinition:
    def __init__(self, native_type: str, python_type: type, constraints: dict = None):
        self.native_type = native_type
        self.python_type = python_type
        self.constraints = constraints or {}