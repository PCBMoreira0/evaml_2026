import sys

import time

from rich import print


def node_processing(node, memory, client_mqtt):
    """ Função de tratamento do nó """
        
    print("[b white]State: Setting [/]the [b white] light effects=" + node.get("mode") + "[/].")

    return node # It returns the same node