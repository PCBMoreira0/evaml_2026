from rich import print

import sys

import os

import time

import config

import play_audio

from base_command_handler import BaseCommandHandler
from robot_package import robot_profile


class CommandHandler(BaseCommandHandler):

    def __init__(self, xml_node, communicator_obj):

        super().__init__(self, communicator_obj)

    def node_process(self, xml_node, memory):
        """Função de tratamento do nó"""

        base_topic = memory.get_base_topic()

        if base_topic == config.TERMINAL_BASE_TOPIC:
            if xml_node.get("block") == "TRUE":
                print(
                    '[b white]State:[/][b white] Playing[/] ▶️  the sound [bold][b white]"'
                    + xml_node.get("source")
                    + '"[/] in [b white]BLOCKING[/] mode.'
                )
                try:
                    play_audio_obj = (
                        play_audio.create_audio_player()
                    )  # Gets the correct class to the current OS.
                    play_audio_obj.play(
                        xml_node,
                        os.getcwd()
                        + "/"
                        + config.ROBOT_PACKAGE_FOLDER
                        + "/audio_module/audio_files/"
                        + xml_node.get("source")
                        + ".wav",
                        block=True,
                    )
                except FileNotFoundError as e:
                    print(e)
                    print(
                        '[b white on red blink] FATAL ERROR [/]: [b yellow reverse] There was a problem playing the audio file [/]: [b wh"'
                        + xml_node.get("source")
                        + '"[/]. Check if it [b white u]exists[/] or is in the [b white u]correct format[/] (wav).✋⛔️'
                    )
                    exit(1)
            else:
                print(
                    '[b white]State:[/][b white] Playing[/] ▶️  the sound [bold][b white]"'
                    + xml_node.get("source")
                    + '"[/] in [b white]NON-BLOCKING[/] mode.'
                )
                try:
                    play_audio_obj = play_audio.create_audio_player()
                    play_audio_obj.play(
                        xml_node,
                        os.getcwd()
                        + "/"
                        + config.ROBOT_PACKAGE_FOLDER
                        + "/audio_module/audio_files/"
                        + xml_node.get("source")
                        + ".wav",
                        block=False,
                    )
                except FileNotFoundError as e:
                    print(
                        '[b white on red blink] FATAL ERROR [/]: [b yellow reverse] There was a problem playing the audio file [/]: [b wh"'
                        + xml_node.get("source")
                        + '"[/]. Check if it [b white u]exists[/] or is in the [b white u]correct format[/] (wav).✋⛔️'
                    )
                    exit(1)

        elif base_topic == robot_profile.ROBOT_BASE_TOPIC:
            if xml_node.get("block") == "TRUE":  # Blocking mode.
                print(
                    '[b white]State:[/][b white] Playing[/] ▶️  the sound [bold][b white]"'
                    + xml_node.get("source")
                    + '"[/] in [b white]BLOCKING[/] mode.'
                )
                message = xml_node.get("source") + "|" + xml_node.get("block")
                self.send(topic_base=base_topic, mqtt_message=message)
                self.receive()  # Wait for the audio to finish playing.

            else:  # Non-blocking mode.
                print(
                    '[b white]State:[/][b white] Playing[/] ▶️  the sound [bold][b white]"'
                    + xml_node.get("source")
                    + '"[/] in [b white]NON-BLOCKING[/] mode.'
                )
                message = xml_node.get("source") + "|" + xml_node.get("block")
                self.send(topic_base=base_topic, mqtt_message=message)

        return xml_node  # It returns the same node
