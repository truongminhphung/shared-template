

class ResourceNotFound(Exception):
    """Exception raised when a database item is not found."""
    def __init__(self, entity_name: str, entity_id: int) -> None:
        self.entity_name = entity_name
        self.entity_id = entity_id
        self.message = f"{entity_name} with ID {entity_id} not found"
        super().__init__(self.message)

class DuplicateResource(Exception):
    """Exception raised when attempting to create a duplicate database item."""
    def __init__(self, entity_name: str, field_name: str, field_value: str) -> None:
        self.entity_name = entity_name
        self.field_name = field_name
        self.field_value = field_value
        self.message = f"{entity_name} with {field_name} '{field_value}' already exists"
        super().__init__(self.message)

class ValidationError(Exception):
    """Exception raised when validation fails."""
    def __init__(self, field: str, message: str) -> None:
        self.field = field
        self.message = message
        super().__init__(self.message)
