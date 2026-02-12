from script_engine import ScriptEngine

sp1 = ScriptEngine() # Empty state.

if not (sp1.load_script("eva_scripts/teste_light_evaml.xml")): # If file was loaded, it is in a Not_Init state.
    # We have a problem with the file.
    exit(1)

sp1.initialize() # After initialization it is in Idle state.


# TERMINAL MODE
sp1.start_script("terminal") # Now, it is in Play state.

while sp1.get_state() == "PLAY": # It is in Play until the script finish. When finished, it will be in Idle state, again.
    sp1.play_next()


# SIMULATOR MODE
sp1.start_script("simulator") # Now, it is in Play state.

while sp1.get_state() == "PLAY": # It is in Play until the script finish. When finished, it will be in Idle state, again.
    sp1.play_next()


# ROBOT MODE
sp1.start_script("robot") # Now, it is in Play state.

while sp1.get_state() == "PLAY": # It is in Play until the script finish. When finished, it will be in Idle state, again.
    sp1.play_next()



