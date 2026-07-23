from rich import print

import json

import ast

from base_command_handler import BaseCommandHandler

import robot_profile  # Module with network device configurations.


class CommandHandler(BaseCommandHandler):

    def __init__(self, xml_node, communicator_obj):
        
        super().__init__(self, communicator_obj)

    def node_process(self, xml_node, memory):
        """ Node process function """


        if xml_node.get("profile") != None:
            if xml_node.get("profile") == "NEUTRAL":
                memory.set_empathy("0.30")
                memory.set_decay("0.70")
                bm = {
                    "valence": "0.00",
                    "arousal": "0.00",
                    "dominance": "0.00"
                }
                memory.set_base_mood(json.dumps(bm))
                memory.set_decay_delay("2.00")

            elif xml_node.get("profile") == "EMPATHETIC":
                memory.set_empathy("1.0")
                memory.set_decay("0.8")
                bm = {
                    "valence": "0.20",
                    "arousal": "0.10",
                    "dominance": "0.00"
                }
                memory.set_base_mood(json.dumps(bm))
                memory.set_decay_delay("3.0")

            elif xml_node.get("profile") == "THERAPIST":
                memory.set_empathy("0.50")
                memory.set_decay("0.70")
                bm = {
                    "valence": "0.00",
                    "arousal": "0.00",
                    "dominance": "0.00"
                }
                memory.set_base_mood(json.dumps(bm))
                memory.set_decay_delay("2.0")

            elif xml_node.get("profile") == "OPTIMISTIC":
                memory.set_empathy("0.30")
                memory.set_decay("1.0")
                bm = { # Verificar esta posição no espaço de acordo com o artigo.
                    "valence": "0.40",
                    "arousal": "0.30",
                    "dominance": "0.20"
                }
                memory.set_base_mood(json.dumps(bm))
                memory.set_decay_delay("3.0")

            elif xml_node.get("profile") == "MELANCHOLIC":
                memory.set_empathy("0.10")
                memory.set_decay("0.08")
                bm = {
                    "valence": "-0.30",
                    "arousal": "-0.30",
                    "dominance": "-0.50"
                }
                memory.set_base_mood(json.dumps(bm))
                memory.set_decay_delay("2.0")
            else:
                # Profile not found...
                exit(1)
        else:
            xml_node.set("profile", "UNCATEGORIZED")
            memory.set_empathy(xml_node.get("empathy"))
            memory.set_decay(xml_node.get("decay"))
            memory.set_decay_delay(xml_node.get("decayDelay"))
            v, a, d = ast.literal_eval(xml_node.get("baseMood"))
            bm = {
                    "valence": v,
                    "arousal": a,
                    "dominance": d
                }
            memory.set_base_mood(json.dumps(bm))

        print("[b white]STATE: Setting [/]the [b white]robot affective profile=" + xml_node.get("profile") + "[/].")
        print("[b white]STATE: Setting [/]the [b white]robot empathy=" + memory.get_empathy() + "[/].")
        print("[b white]STATE: Setting [/]the [b white]robot emotional decay=" + memory.get_decay() + "[/].")
        print("[b white]STATE: Setting [/]the [b white]robot emotional decay delay=" + memory.get_decay_delay() + "[/].")
        print("[b white]STATE: Setting [/]the [b white]robot base mood (VAD vector)=" + memory.get_base_mood() + "[/].")
                
        base_topic = memory.get_base_topic()
 
        # values = [float(x) for x in memory.get_base_mood().strip("[]").split(",")]

        base_mood = json.loads(memory.get_base_mood())
        message = {
            "profile": xml_node.get("profile"),
            "empathy": memory.get_empathy(),
            "decay": memory.get_decay(),
            "delay": memory.get_decay_delay(),
            "mood": {
                "valence": base_mood["valence"],
                "arousal": base_mood["arousal"],
                "dominance": base_mood["dominance"]
            }
        }

        message = json.dumps(message)
        # message = xml_node.get('profile') + "|" + memory.get_empathy() + "|" + memory.get_decay() + "|" + memory.get_base_mood()
        

        if base_topic == robot_profile.SIMULATOR_BASE_TOPIC or base_topic == robot_profile.ROBOT_BASE_TOPIC:
            self.send(topic_base=base_topic, mqtt_message=message)

        return xml_node # It returns the same node
        