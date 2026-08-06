from affective_input import AffectiveInput

class TerInput(AffectiveInput):
    def __init__(self) -> None:
        super().__init__("TER")
        self.observations = []

    def collect(self, text: str) -> None:
        if not self.active:
            return

        # RoBERTa, another transformer, lexicon, LLM, etc.
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