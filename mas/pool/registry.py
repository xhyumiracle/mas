from typing import Generic, TypeVar, Callable, Optional

T = TypeVar("T")

class RegistryContext(Generic[T]):
    def __init__(self):
        self._active: Optional[T] = None

    def set(self, instance: T):
        self._active = instance

    def get(self) -> T:
        if self._active is None:
            raise RuntimeError("RegistryContext is not initialized.")
        return self._active