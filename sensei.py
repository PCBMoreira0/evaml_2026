import argparse

from script_engine import ScriptEngine

parser = argparse.ArgumentParser(
    description="Sensei - Script Execution and Simulation for Empathic Interaction")

parser.add_argument(
    "-script",
    type=str,
    required=True,
    help="Path to the EVAML script (.xml)"
)

parser.add_argument(
    "-mode",
    choices=["terminal", "simulator", "robot"],
    required=True,
    help="Execution mode"
)

args = parser.parse_args()

script = args.script
mode = args.mode

sp1 = ScriptEngine() # Empty state.

if not (sp1.load_script(script)): # If file was loaded, it is in a Not_Init state.
    # We have a problem with the file. eva_scripts/tabuada_nova_evaml.xml
    exit(1)

sp1.initialize() # After initialization it is in Idle state.

sp1.start_script(mode) # Now, it is in Play state.

while sp1.get_state() == "PLAY": # It is in Play until the script finish. When finished, it will be in Idle state, again.
    sp1.play_next()





