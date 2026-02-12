import sys
from abc import ABC, abstractmethod
import os
import subprocess

import config
from rich import print

# Classe base que define o contrato ds classes que tocam audio
class PlayAudioBase(ABC):
    @abstractmethod
    def play(self):
        pass


# Implementação para Linux
class LinuxPlayAudio(PlayAudioBase):
    def play(self, xml_node, file_name, block):
        audio_file = file_name
        try:
            if not os.path.exists(audio_file):
                raise FileNotFoundError(f"Arquivo não encontrado: {audio_file}")
            if block == True:
                play = subprocess.Popen(['play', '-q', audio_file], stdout=subprocess.PIPE)
                play.communicate()[0]
                return True
            else:
                play = subprocess.Popen(['play', '-q', audio_file], stdout=subprocess.PIPE)
                return True

        except FileNotFoundError as e:
            print(audio_file)
            print('[b white on red blink] FATAL ERROR [/]: [b yellow reverse] There was a problem playing the audio file [/]: [b white]"' + xml_node.get("source") + '"[/]. Check if it [b u white]exists[/] or is in the [b u white]correct format[/] (wav).✋⛔️')
            return False
            


# Implementação para Windows
class WindowsPlayAudio(PlayAudioBase):
    def play(self, xml_node, file_name):
        print("Executando o método 'play' usando a classe Windows... (Falta implementar!!!)")


# Cria a intância adequada ao Sistema Operacional
def create_audio_player():
    os_atual = sys.platform
    if os_atual.startswith('linux'):
        return LinuxPlayAudio()
    elif os_atual.startswith('win'):
        return WindowsPlayAudio()
    else:
        raise ValueError("Sistema operacional não suportado.")
