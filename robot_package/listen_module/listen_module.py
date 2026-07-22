import sounddevice as sd
import speech_recognition as sr


from rich import print
from rich.console import Console

console = Console()

import robot_profile  # Module with network device configurations.

import config

from base_command_handler import BaseCommandHandler

recognizer = sr.Recognizer()
microphone = sr.Microphone(chunk_size = 64)
threshold = 980 # Regulates the sensitivity between speech and silence. A good value tested in my house was 980.
# timeout = 10

# r.dynamic_energy_threshold = False
recognizer.energy_threshold = threshold # Audio capture sensitivity.


class CommandHandler(BaseCommandHandler):

    def __init__(self, xml_node, communicator_obj):
        
        super().__init__(self, communicator_obj)

# Função de bloqueio que é usada para sincronia entre os módulos e o Script Player
# def block(state, memory, client_mqtt):
#     memory.robot_state = state # Altera o estado do robô.
#     client_mqtt.publish(topic_base + "/leds", "LISTEN")
#     while memory.robot_state != "free": # Aguarda que o robô fique livre para seguir para o próximo comando.
#         time.sleep(0.01)
#     client_mqtt.publish(topic_base + "/leds", "STOP")


    def node_process(self, xml_node, memory):
        """ Node handling function """
        

        base_topic = memory.get_base_topic()
        

        # if base_topic == config.TERMINAL_BASE_TOPIC or base_topic == config.SIMULATOR_BASE_TOPIC:
        #     # client_mqtt.publish(topic_base + "/leds", "STOP")
        #     if xml_node.get("var") == None: # Maintains compatibility with the use of the $ variable
        #         print('[b white]STATE:[/] The Robot is [b green]listening[/] in [b white]' + xml_node.get("language") + '[/]. It will be stored in [b white]$[/] ', end="")
        #         # memory.var_dollar.append([user_answer, "<listen>"])
        #         user_answer = console.input("[b white on green blink] > [/] ")
        #         memory.setDollar([user_answer, "<listen>"])
        #     else:
        #         var_name = xml_node.get("var")
        #         print('[b white]STATE:[/] The Robot is [b green]listening[/] in [b white]' + xml_node.get("language") + '[/]. It will be stored in [b white]' + var_name + '[/] ', end="")
        #         # memory.vars[var_name] = user_answer
        #         user_answer = console.input("[b white on green blink] > [/] ")
        #         memory.setVar(var_name, user_answer)
        

        # Captura com o modelo local Whisper
        # A lib Whisper foi instalada
        # pip install openai-whisper
        #
        # O Speech Recognizer (recognize_whisper) carrega o model base automaticamente por trás dos panos
        # 
        # A qualidade é muito boa e retorna texto com pontuação.
        # Mas a velocidade é menor do que o modelo online do Google, demora tipo o dobro do tempo
        # 
        


        # 
        # Captura de voz e Speech to text usando o Google
        #
        # Tudo funcionando no código abaixo usando o Google
        with microphone as source:
            print("The robot is listening!")
            audio = recognizer.listen(source)
            # print("The audio was recorded and it will send to the cloud!")
            # language_defined_by_user = "pt-BR"
            language_defined_by_user = "en-US"
            try:
                # Recognizes speech using Google Speech Recognition. ("pt-BR", "en-US", "es-ES")
                response = recognizer.recognize_google(audio, language = language_defined_by_user)
                print("Speech-To-Text: " + response)

                if xml_node.get("var") == None: # Maintains compatibility with the use of the $ variable
                    # print('[b white]STATE:[/] The Robot is [b green]listening[/] in [b white]' + xml_node.get("language") + '[/]. It will be stored in [b white]$[/] ', end="")
                    # # memory.var_dollar.append([user_answer, "<listen>"])
                    # user_answer = console.input("[b white on green blink] > [/] ")
                    memory.setDollar([response, "<listen>"])
                else:
                    var_name = xml_node.get("var")
                    # print('[b white]STATE:[/] The Robot is [b green]listening[/] in [b white]' + xml_node.get("language") + '[/]. It will be stored in [b white]' + var_name + '[/] ', end="")
                    # # memory.vars[var_name] = user_answer
                    # user_answer = console.input("[b white on green blink] > [/] ")
                    memory.setVar(var_name, response)

                
            except sr.UnknownValueError:
                print("Google Speech Recognition could not understand your audio...")

            except sr.RequestError as e:
                print("Unable to request the results from Google Speech Recognition: {0}".format(e))


        
  
            
        # Controls the physical robot.
        if memory.running_mode == "robot": 
            pass
            # client = create_mqtt_client()
            # client.publish(robot_topic_base + '/' + xml_node.tag, message)

        return xml_node # It returns the same node

