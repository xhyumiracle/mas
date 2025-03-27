class GraphValidationError(Exception):
    pass

class InvalidNodeError(GraphValidationError):
    pass

class ModalityMismatchError(GraphValidationError):
    pass