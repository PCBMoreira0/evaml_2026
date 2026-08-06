from abc import ABC, abstractmethod
from typing import Any


class AffectiveInput(ABC):
    """Contract for affective perception input modules."""

    def __init__(self, source_id: str) -> None:
        if not source_id.strip():
            raise ValueError("source_id cannot be empty.")

        self.source_id = source_id
        self.active = False

    def start_window(self) -> None:
        """Starts a new perception window."""
        self.reset()
        self.active = True

    def end_window(self) -> dict[str, Any] | None:
        """
        Ends the current window and returns one final observation.

        Returns None when no valid observation was produced.
        """
        self.active = False
        return self.build_observation()

    @abstractmethod
    def collect(self, data: Any) -> None:
        """Processes one input sample while the window is active."""
        raise NotImplementedError

    @abstractmethod
    def build_observation(self) -> dict[str, Any] | None:
        """Builds the final CAT or VAD observation for PULSE."""
        raise NotImplementedError

    @abstractmethod
    def reset(self) -> None:
        """Clears all state from the previous perception window."""
        raise NotImplementedError