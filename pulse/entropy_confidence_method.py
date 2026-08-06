from confidence_method import ConfidenceMethod

import math
from typing import Any


class EntropyConfidenceMethod(ConfidenceMethod):

    def estimate(
        self,
        observations: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:

        for observation in observations:
            if observation["representation"] != "CAT":
                continue

            probabilities = observation["probabilities"].values()

            entropy = -sum(
                probability * math.log2(probability)
                for probability in probabilities
                if probability > 0
            )

            maximum_entropy = math.log2(
                len(observation["probabilities"])
            )

            observation["confidence"] = (
                1.0 - entropy / maximum_entropy
            )

        return observations
    