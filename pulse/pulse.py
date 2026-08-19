from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

from paho.mqtt import client as mqtt_client

# ---------------------------------------------------------------------------
# Project paths
# ---------------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
PARENT_DIR = BASE_DIR.parent

if str(PARENT_DIR) not in sys.path:
    sys.path.append(str(PARENT_DIR))

ROBOT_PACKAGE_DIR = PARENT_DIR / "robot_package"

if str(ROBOT_PACKAGE_DIR) not in sys.path:
    sys.path.append(str(ROBOT_PACKAGE_DIR))

import config
import robot_package.robot_profile as robot_profile

# Adjust these imports to match the actual names and locations of your files.
from confidence_method import ConfidenceMethod
from entropy_confidence_method import EntropyConfidenceMethod
from fusion_method import FusionMethod
from weighted_fusion_method import WeightedFusionMethod


AffectiveObservation = dict[str, Any]
VADState = dict[str, float]


class Pulse:
    """
    Coordinates perception windows and estimates the user's affective state.

    Confidence estimation and multimodal fusion are supplied as replaceable
    objects through constructor-based dependency injection.
    """

    VAD_REFERENCE: dict[str, tuple[float, float, float]] = {
        "happiness": (0.76, 0.48, 0.35),
        "sadness": (-0.63, -0.27, -0.33),
        "anger": (-0.43, 0.67, 0.34),
        "fear": (-0.64, 0.60, -0.43),
        "surprise": (0.40, 0.67, -0.13),
        "disgust": (-0.60, 0.35, 0.11),
        "neutral": (0.00, 0.00, 0.00),
    }

    def __init__(
        self,
        confidence_method: ConfidenceMethod,
        fusion_method: FusionMethod,
    ) -> None:
        if not isinstance(confidence_method, ConfidenceMethod):
            raise TypeError(
                "confidence_method must implement ConfidenceMethod."
            )

        if not isinstance(fusion_method, FusionMethod):
            raise TypeError(
                "fusion_method must implement FusionMethod."
            )

        self._confidence_method = confidence_method
        self._fusion_method = fusion_method

        self._sources_to_receive: list[str] = []
        self._affective_observations: list[AffectiveObservation] = []

    @property
    def pending_sources(self) -> tuple[str, ...]:
        """Returns the sources still expected in the current window."""
        return tuple(self._sources_to_receive)

    @property
    def observations(self) -> tuple[AffectiveObservation, ...]:
        """Returns the observations collected in the current window."""
        return tuple(self._affective_observations)

    def start_perception_window(self, sources: list[str]) -> None:
        """
        Starts a new perception window.

        A copy of the source list is stored to prevent external modifications.
        Previous observations are discarded.
        """
        if not isinstance(sources, list):
            raise TypeError("sources must be a list.")

        normalized_sources = [
            str(source).strip()
            for source in sources
            if str(source).strip()
        ]

        if not normalized_sources:
            raise ValueError(
                "The perception window must contain at least one source."
            )

        if len(normalized_sources) != len(set(normalized_sources)):
            raise ValueError(
                "The perception source list contains duplicated values."
            )

        self._sources_to_receive = normalized_sources.copy()
        self._affective_observations.clear()

        print(
            "Sources to be received in the perception window: "
            f"{self._sources_to_receive}"
        )

    def receive_observation(
        self,
        observation: AffectiveObservation,
    ) -> VADState | None:
        """
        Receives one affective observation.

        Returns the fused VAD state when all expected sources have responded.
        Otherwise, returns None.
        """
        self._validate_observation(observation)

        source = observation["source"]

        if source not in self._sources_to_receive:
            print(
                f"Observation from source '{source}' ignored. "
                "The source is not pending in the current perception window."
            )
            return None

        print(f"Source {source} received.")

        self._sources_to_receive.remove(source)
        self._affective_observations.append(observation.copy())

        if self._sources_to_receive:
            print(
                "Waiting for remaining sources: "
                f"{self._sources_to_receive}"
            )
            return None

        return self._process_observations()

    def _process_observations(self) -> VADState:
        """
        Executes the fixed PULSE processing pipeline.

        The confidence and fusion stages are delegated to replaceable objects.
        """
        if not self._affective_observations:
            raise ValueError("No affective observations were provided.")

        print("1) Estimating confidence...")
        observations_with_confidence = (
            self._confidence_method.estimate(
                self._affective_observations
            )
        )

        if observations_with_confidence is not None:
            self._affective_observations = (
                observations_with_confidence
            )

        print("2) Converting categorical observations to VAD...")
        self._cat_to_vad_conversion()

        print("3) Fusing observations...")
        user_affective_state = self._fusion_method.fuse(
            self._affective_observations
        )

        return self._normalize_vad_state(user_affective_state)

    def _cat_to_vad_conversion(self) -> None:
        """
        Converts CAT observations into VAD observations.

        VAD observations are preserved without modification.
        """
        for observation in self._affective_observations:
            if observation["representation"] != "CAT":
                continue

            probabilities = observation["probabilities"]

            valence = 0.0
            arousal = 0.0
            dominance = 0.0

            for emotion, probability in probabilities.items():
                if emotion not in self.VAD_REFERENCE:
                    raise ValueError(
                        f"Unknown categorical emotion: {emotion}"
                    )

                v_ref, a_ref, d_ref = self.VAD_REFERENCE[emotion]

                probability_value = float(probability)

                valence += probability_value * v_ref
                arousal += probability_value * a_ref
                dominance += probability_value * d_ref

            observation["representation"] = "VAD"
            observation["values"] = {
                "valence": valence,
                "arousal": arousal,
                "dominance": dominance,
            }

            observation.pop("probabilities", None)

            print("VAD conversion:", observation)

    @staticmethod
    def _normalize_vad_state(state: VADState) -> VADState:
        """Validates and rounds the final VAD state."""
        required_dimensions = {
            "valence",
            "arousal",
            "dominance",
        }

        if not isinstance(state, dict):
            raise TypeError(
                "The fusion method must return a dictionary."
            )

        missing_dimensions = required_dimensions - state.keys()

        if missing_dimensions:
            raise ValueError(
                "The fusion result is missing dimensions: "
                f"{sorted(missing_dimensions)}"
            )

        return {
            "valence": round(float(state["valence"]), 2),
            "arousal": round(float(state["arousal"]), 2),
            "dominance": round(float(state["dominance"]), 2),
        }

    @staticmethod
    def _validate_observation(
        observation: AffectiveObservation,
    ) -> None:
        """Validates the common structure of a PULSE input observation."""
        if not isinstance(observation, dict):
            raise TypeError("The observation must be a dictionary.")

        if not observation:
            raise ValueError("An empty observation was received.")

        required_fields = {
            "source",
            "representation",
        }

        missing_fields = required_fields - observation.keys()

        if missing_fields:
            raise ValueError(
                "The observation is missing fields: "
                f"{sorted(missing_fields)}"
            )

        representation = observation["representation"]

        if representation not in {"CAT", "VAD"}:
            raise ValueError(
                "representation must be either 'CAT' or 'VAD'."
            )

        if representation == "CAT":
            if "probabilities" not in observation:
                raise ValueError(
                    "A CAT observation must contain probabilities."
                )

            probabilities = observation["probabilities"]

            if not isinstance(probabilities, dict):
                raise TypeError(
                    "probabilities must be a dictionary."
                )

            if not probabilities:
                raise ValueError(
                    "The probability distribution cannot be empty."
                )

        if representation == "VAD":
            if "values" not in observation:
                raise ValueError(
                    "A VAD observation must contain values."
                )

            values = observation["values"]

            if not isinstance(values, dict):
                raise TypeError(
                    "values must be a dictionary."
                )

            for dimension in (
                "valence",
                "arousal",
                "dominance",
            ):
                if dimension not in values:
                    raise ValueError(
                        "The VAD observation is missing "
                        f"the '{dimension}' dimension."
                    )

            if "confidence" not in observation:
                raise ValueError(
                    "A VAD observation must provide confidence."
                )


class PulseMqttApplication:
    """
    Connects the PULSE processing component to the MQTT broker.
    """

    def __init__(
        self,
        pulse: Pulse,
        broker: str,
        port: int,
        robot_base_topic: str,
    ) -> None:
        self._pulse = pulse
        self._broker = broker
        self._port = port
        self._robot_base_topic = robot_base_topic.rstrip("/")

        self._perception_topic = (
            f"{self._robot_base_topic}/PERCEPTION"
        )
        self._input_topic = (
            f"{self._robot_base_topic}/PULSE/INPUT"
        )
        self._output_topic = (
            f"{self._robot_base_topic}/USER_AFFECTIVE_STATE"
        )

        self._client = mqtt_client.Client()

        self._client.on_connect = self._on_connect
        self._client.on_message = self._on_message

    def _on_connect(
        self,
        client: mqtt_client.Client,
        userdata: Any,
        flags: dict[str, Any],
        rc: int,
    ) -> None:
        if rc != 0:
            print(
                "PULSE connected to MQTT with error code "
                f"{rc}."
            )
            return

        client.subscribe(
            [
                (self._input_topic, 1),
                (self._perception_topic, 1),
            ]
        )

        print(
            "PULSE - Perception and Unification Layer "
            "for State Estimation - Connected."
        )

    def _on_message(
        self,
        client: mqtt_client.Client,
        userdata: Any,
        msg: Any,
    ) -> None:
        try:
            message = json.loads(
                msg.payload.decode("utf-8")
            )

            if msg.topic == self._perception_topic:
                self._handle_perception_message(message)
                return

            if msg.topic == self._input_topic:
                self._handle_input_message(message)
                return

            print(f"Unexpected MQTT topic: {msg.topic}")

        except json.JSONDecodeError as error:
            print(
                f"Invalid JSON received on topic {msg.topic}: "
                f"{error}"
            )

        except (
            KeyError,
            TypeError,
            ValueError,
        ) as error:
            print(
                f"Invalid PULSE message on topic {msg.topic}: "
                f"{error}"
            )

        except Exception as error:
            print(
                "Unexpected error while processing MQTT message: "
                f"{error}"
            )

    def _handle_perception_message(
        self,
        message: dict[str, Any],
    ) -> None:
        action = message.get("action")

        if action == "START":
            sources = message.get("sources")

            if sources is None:
                raise ValueError(
                    "A PERCEPTION START message must provide sources."
                )

            self._pulse.start_perception_window(sources)
            return

        if action == "END":
            # In the current implementation, fusion starts when every expected
            # source has provided an observation. END requires no additional
            # action.
            print("Perception window END received.")
            return

        raise ValueError(
            f"Unknown PERCEPTION action: {action}"
        )

    def _handle_input_message(
        self,
        message: AffectiveObservation,
    ) -> None:
        user_affective_state = (
            self._pulse.receive_observation(message)
        )

        if user_affective_state is None:
            return

        self._publish_user_affective_state(
            user_affective_state
        )

    def _publish_user_affective_state(
        self,
        user_affective_state: VADState,
    ) -> None:
        payload = json.dumps(
            user_affective_state,
            ensure_ascii=False,
        )

        result = self._client.publish(
            self._output_topic,
            payload,
            qos=1,
        )

        if result.rc != mqtt_client.MQTT_ERR_SUCCESS:
            raise RuntimeError(
                "Unable to publish USER_AFFECTIVE_STATE. "
                f"MQTT error code: {result.rc}"
            )

        print(
            "User affective state published on "
            f"{self._output_topic}: "
            f"{user_affective_state}"
        )

    def run(self) -> None:
        try:
            self._client.connect(
                self._broker,
                self._port,
            )
        except Exception as error:
            print(
                "Unable to connect to the MQTT broker: "
                f"{error}"
            )
            raise SystemExit(1) from error

        try:
            self._client.loop_forever()
        except KeyboardInterrupt:
            print("\nStopping PULSE...")
        finally:
            self._client.disconnect()


def create_pulse() -> Pulse:
    """
    Creates PULSE with the default processing methods.

    To use other implementations, replace only the objects created here.
    """
    confidence_method = EntropyConfidenceMethod()
    fusion_method = WeightedFusionMethod()

    return Pulse(
        confidence_method=confidence_method,
        fusion_method=fusion_method,
    )


def main() -> None:
    pulse = create_pulse()

    application = PulseMqttApplication(
        pulse=pulse,
        broker=config.MQTT_BROKER_ADRESS,
        port=config.MQTT_PORT,
        robot_base_topic=robot_profile.ROBOT_BASE_TOPIC,
    )

    application.run()


if __name__ == "__main__":
    main()