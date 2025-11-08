class DomainError(Exception):
    """Excepción base para errores de lógica de negocio."""
    pass

class InvalidReviewError(DomainError):
    """Lanzada cuando los datos de una Review son inválidos."""
    pass

class InvalidClassificationError(DomainError):
    """Lanzada cuando se intenta usar una clasificación que no es válida."""
    pass