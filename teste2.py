from script_engine import ScriptEngine

sp2 = ScriptEngine() # Empty state.

if not (sp2.load_script("eva_scripts/pcb2_evaml.xml")): # If file was loaded, it is in a Not_Init state.
    # We have a problem with the file.
    exit(1)

sp2.initialize(True) # After initialization it is in Idle state.

sp2.start_script("terminal-plus") # Now, it is in Play state.

while sp2.get_state() == "PLAY": # It is in Play until the script finish. When finished, it will be in Idle state, again.
    sp2.play_next()

