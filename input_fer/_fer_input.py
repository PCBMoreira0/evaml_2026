from affective_input import AffectiveInput

class FerInput(AffectiveInput):
    def __init__(self) -> None:
        super().__init__("FER")
        self.observations = []

    def collect(self, frame) -> None:
        if not self.active:
            return

        # DeepFace, another FER model, or another technique.
        result = ...
        self.observations.append(result)

    def build_observation(self) -> dict | None:
        if not self.observations:
            return None

        probabilities = self._aggregate()

        return {
            "source": self.source_id,
            "representation": "CAT",
            "probabilities": probabilities,
        }

    def reset(self) -> None:
        self.observations.clear()