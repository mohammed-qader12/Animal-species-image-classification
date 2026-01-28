from abc import ABC, abstractmethod
from typing import Any

class ModelRepository(ABC):
    """
    Abstract interface for searching/saving/loading models.
    """

    @abstractmethod
    def save(self, model: Any, name: str):
        pass

    @abstractmethod
    def load(self, name: str) -> Any:
        pass
