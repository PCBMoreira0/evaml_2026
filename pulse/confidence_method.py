from abc import ABC, abstractmethod
from typing import Any


class ConfidenceMethod(ABC):

    @abstractmethod
    def estimate(self, observations: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Assign confidence values to the observations."""
        raise NotImplementedError