from mas.errors.orch_error import OrchestrationError

class GraphValidationError(OrchestrationError):
    pass

class InvalidNodeError(GraphValidationError):
    pass

class ModalityMismatchError(GraphValidationError):
    pass