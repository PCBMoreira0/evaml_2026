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
    def play(self, xml_node, text_to_speech, file_name):
        audio_path_and__file = "robot_package/talk_module/tts_cache_files/" + file_name + config.WATSON_AUDIO_EXTENSION
        try:
            if not os.path.exists(audio_path_and__file):
                raise FileNotFoundError(f"Arquivo não encontrado: {audio_path_and__file}")
            print('[b white]State:[/] The Robot is [b blue]speaking[/] the sentence: [b white]"' + text_to_speech + '[/]"')
            play = subprocess.Popen(['play', '-q', audio_path_and__file], stdout=subprocess.PIPE)
            play.communicate()[0]
            return True

        except FileNotFoundError as e:
            print('[b white on red blink] FATAL ERROR [/]: [b yellow reverse] There was a problem playing the audio file [/]: [b white]"' + xml_node.get("source") + '"[/]. Check if it [b u white]exists[/] or is in the [b u white]correct format[/] (wav)[/].✋⛔️')
            return False
            # exit(1) 


# Implementação para Windows
class WindowsPlayAudio(PlayAudioBase):
    def play(self, xml_node,  text_to_speech, file_name):
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