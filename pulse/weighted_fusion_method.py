from fusion_method import FusionMethod

from typing import Any

class WeightedFusionMethod(FusionMethod):

    def fuse(
        self,
        observations: list[dict[str, Any]]
    ) -> dict[str, float]:

        if not observations:
            raise ValueError("No observations were provided.")

        total_confidence = sum(
            observation["confidence"]
            for observation in observations
        )

        if total_confidence <= 0:
            raise ValueError(
                "The total confidence must be greater than zero."
            )

        dimensions = ("valence", "arousal", "dominance")

        return {
            dimension: round(
                sum(
                    observation["confidence"]
                    * observation["values"][dimension]
                    for observation in observations
                )
                / total_confidence,
                2,
            )
            for dimension in dimensions
        }