import sys

import time

from rich import print


def node_processing(node, memory, client_mqtt):
    """ Função de tratamento do nó """
    memory.default_voice = node.get("type")
    if node.get("pitchShift") != None:
        memory.default_voice_pitch_shift = node.get("pitchShift")
    else:
        memory.default_voice_pitch_shift = "0"
        
        
    print("[b white]State: Setting [/]the robot default[b white] voice=" + node.get("type") + "[/], with [b white]pitch shift=" + node.get("pitchShift") + "[/].")

    return node # It returns the same node