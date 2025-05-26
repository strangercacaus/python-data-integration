from typing import Dict
from ....types.base import DataType, TypeDefinition

# Define common constraints
STRING_CONSTRAINTS = {"max_length": None}
NUMBER_CONSTRAINTS = {"min": None, "max": None}

POSTGRESQL_TYPES: Dict[DataType, TypeDefinition] = {
    DataType.STRING: TypeDefinition(
        native_type="text",
        python_type=str,
        constraints=STRING_CONSTRAINTS
    ),
    DataType.INTEGER: TypeDefinition(
        native_type="integer",
        python_type=int,
        constraints=NUMBER_CONSTRAINTS
    ),
    DataType.BIGINTEGER: TypeDefinition(
        native_type="bigint",
        python_type=int,
        constraints=NUMBER_CONSTRAINTS
    ),
    DataType.BIGDECIMAL: TypeDefinition(
        native_type="numeric",
        python_type=float,
        constraints=NUMBER_CONSTRAINTS
    ),
    DataType.SMALLDECIMAL: TypeDefinition(
        native_type="numeric",
        python_type=float,
        constraints=NUMBER_CONSTRAINTS
    ),
    DataType.SMALLINTEGER: TypeDefinition(
        native_type="smallint",
        python_type=int,
        constraints=NUMBER_CONSTRAINTS
    ),
    DataType.DECIMAL: TypeDefinition(
        native_type="numeric",
        python_type=float,
        constraints=NUMBER_CONSTRAINTS
    ),
    DataType.BLOB: TypeDefinition(
        native_type="bytea",
        python_type=bytes,
        constraints=STRING_CONSTRAINTS
    ),
    DataType.BOOLEAN: TypeDefinition(
        native_type="boolean",
        python_type=bool,
        constraints=STRING_CONSTRAINTS
    ),
    DataType.DATE: TypeDefinition(
        native_type="date",
        python_type=str,
        constraints=STRING_CONSTRAINTS
    ),
    DataType.DATETIME: TypeDefinition(
        native_type="timestamp",
        python_type=str,
        constraints=STRING_CONSTRAINTS
    ),
    DataType.CHAR: TypeDefinition(
        native_type="char",
        python_type=str,
        constraints=STRING_CONSTRAINTS
    ),
    DataType.VARCHAR: TypeDefinition(
        native_type="varchar",
        python_type=str,
        constraints=STRING_CONSTRAINTS
    ),
    DataType.BYTE: TypeDefinition(
        native_type="byte",
        python_type=bytes,
        constraints=STRING_CONSTRAINTS
    ),
    DataType.BINARY: TypeDefinition(
        native_type="binary",
        python_type=bytes,
        constraints=STRING_CONSTRAINTS
    ),
    DataType.LONGBLOB: TypeDefinition(
        native_type="bytea",
        python_type=bytes,
        constraints=STRING_CONSTRAINTS
    ),
    DataType.LONGVARCHAR: TypeDefinition(
        native_type="varchar",
        python_type=str,
        constraints=STRING_CONSTRAINTS
    ),
    DataType.MEDIUMBLOB: TypeDefinition(
        native_type="bytea",
        python_type=bytes,
        constraints=STRING_CONSTRAINTS
    ),
    DataType.MEDIUMVARCHAR: TypeDefinition(
        native_type="varchar",
        python_type=str,
        constraints=STRING_CONSTRAINTS
    ),
    DataType.TINYBLOB: TypeDefinition(
        native_type="bytea",
        python_type=bytes,
        constraints=STRING_CONSTRAINTS
    ),
    DataType.TINYVARCHAR: TypeDefinition(
        native_type="varchar",
        python_type=str,
        constraints=STRING_CONSTRAINTS
    ),
    DataType.VARCHAR: TypeDefinition(
        native_type="varchar",
        python_type=str,
        constraints={"max_length": None}
    ),
    DataType.CHAR: TypeDefinition(
        native_type="char",
        python_type=str,
        constraints={"max_length": None}
    )
}