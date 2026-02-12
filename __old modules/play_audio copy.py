import platform
import subprocess
import os
 
import config # Module with the constants and parameters used in other modules.

# I stopped using the Playsound library because it was too much trouble!

# Playsound for Linux
if platform.system() == "Linux":
    def playsound(audio_file, block = True):
        if block == True:
            if not os.path.exists(audio_file):
                raise FileNotFoundError(f"Arquivo não encontrado: {audio_file}")
            play = subprocess.Popen(['play', '-q', audio_file], stdout=subprocess.PIPE)
            play.communicate()[0]
                
        else:
            if not os.path.exists(audio_file):
                raise FileNotFoundError(f"Arquivo não encontrado: {audio_file}")
            play = subprocess.Popen(['play', '-q', audio_file], stdout=subprocess.PIPE)
