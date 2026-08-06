from abc import ABC, abstractmethod
from typing import Any


class FusionMethod(ABC):

    @abstractmethod
    def fuse(self, observations: list[dict[str, Any]]) -> dict[str, float]:
        """Fuse VAD observations into a single VAD state."""
        raise NotImplementedError