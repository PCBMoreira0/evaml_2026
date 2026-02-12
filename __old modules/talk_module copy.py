import time

import random as rnd
import re
from rich import print

from play_audio import playsound # Adapter module for the audio library.
# Depending on the OS it matters and defines a function called "playsound".

import config # Module with network device configurations.

import hashlib
import os

# Watson imports
from ibm_watson import TextToSpeechV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import ApiException

import robot_profile  # Module with network device configurations.


robot_topic_base = robot_profile.ROBOT_TOPIC_BASE
broker = config.MQTT_BROKER_ADRESS # Broker address.
port = config.MQTT_PORT # Broker Port.
voice_type = config.VOICE_TYPE



# Watson API configuration key.
with open("robot_package/talk_module/ibm_cred.txt", "r") as ibm_cred: 
    ibm_config = ibm_cred.read().splitlines()
apikey = ibm_config[0]
url = ibm_config[1]

# Setup Watson service.
authenticator = IAMAuthenticator(apikey)

# TTS service.
tts = TextToSpeechV1(authenticator = authenticator)
tts.set_service_url(url)

auth_start_time = time.time() # Time of authentication.
first_requisition = True; # Indicates that this is the first request for the Watson service.




from base_command_handler import BaseCommandHandler

class CommandHandler(BaseCommandHandler):

    def __init__(self, xml_node, communicator_obj):
        
        super().__init__(self, communicator_obj)

    def ibm_watson_init(self):
        


    def node_process(self, xml_node, memory):
        """ Node handling function """

        if memory.running_mode == "simulator":
            topic_base = config.SIMULATOR_TOPIC_BASE
        elif memory.running_mode == "robot":
            topic_base = robot_profile.ROBOT_TOPIC_BASE
        else:
            topic_base = config.TERMINAL_TOPIC_BASE

        # Node processing
        if xml_node.text == None: # There is no text to speech
            print("[b white on red blink] FATAL ERROR [/]: [b yellow reverse] There is no text to speech [/] in the element [b white]<talk>[/]. Please, check your code.✋⛔️")
            exit(1)

        texto = xml_node.text
        palavras = texto.split()
        texto_normalizado = ' '.join(palavras)
        texto = texto_normalizado.replace('\n', '').replace('\r', '').replace('\t', '') # Remove tabulações e salto de linha.
        # Replace variables throughout the text. variables must exist in memory
        if "#" in texto:
            # Checks if the robot's memory (vars) is empty
            if memory.vars == {}:
                print("[b white on red blink] FATAL ERROR [/]: [b yellow reverse] No variables have been defined [/] to be used in the[b white] <talk>[/]. Please, check your code.✋⛔️")
                exit(1)

            var_list = re.findall(r'\#[a-zA-Z_]+[0-9]*', texto) # Generate list of occurrences of vars (#...)
            for v in var_list:
                if v[1:] in memory.vars:
                    texto = texto.replace(v, str(memory.vars[v[1:]]))
                else:
                    # If the variable does not exist in the robot's memory, it displays an error message
                    print("[b white on red blink] FATAL ERROR [/]: The variable [b white]" + v[1:] + "[/] [b yellow reverse] has not been declared [/] to be used in the [b white]<talk>[/]. Please, check your code.✋⛔️")
                    exit(1)

        # This part replaces the $, or the $-1 or the $1 in the text
        if "$" in texto: # Check if there is $ in the text
            # Checks if var_dollar has any value in the robot's memory
            if (len(memory.var_dolar)) == 0:
                print("[b white on red blink] FATAL ERROR [/]: There are [b yellow reverse] no values [/] for the [b white]$[/] used in the [b white]<talk>[/]. Please, check your code.✋⛔️")
                exit(1)
            else: # Find the patterns $ $n or $-n in the string and replace with the corresponding values
                dollars_list = re.findall(r'\$[-0-9]*', texto) # Find dollar patterns and return a list of occurrences
                dollars_list = sorted(dollars_list, key=len, reverse=True) # Sort the list in descending order of length (of the element)
                for var_dollar in dollars_list:
                    if len(var_dollar) == 1: # Is the dollar ($)
                        texto = texto.replace(var_dollar, memory.var_dolar[-1][0])
                    else: # May be of type $n or $-n
                        if "-" in var_dollar: # $-n type
                            indice = int(var_dollar[2:]) # Var dollar is of type $-n. then just take n and convert it to int.
                            try:
                                texto = texto.replace(var_dollar, memory.var_dolar[-(indice + 1)][0]) 
                            except IndexError:
                                print('[b white on red blink] FATAL ERROR [/]: There was an [b yellow reverse] index error [/] for the variable [b white]"' + var_dollar + '"[/]. Please, check your code.✋⛔️')
                                exit(1)
                        else: # tipo $n
                            indice = int(var_dollar[1:]) # Var dollar is of type $n. then just take n and convert it to int.
                            try:
                                texto = texto.replace(var_dollar, memory.var_dolar[(indice - 1)][0])
                            except IndexError:
                                print('[b white on red blink] FATAL ERROR [/]: There was an [b yellow reverse] index error [/] for the variable [b white]"' + var_dollar + '"[/]. Please, check your code.✋⛔️')
                                exit(1)
                            
            
        # This part implements the random text generated by using the / character
        texto = texto.split(sep="/") # Text becomes a list with the number of sentences divided by character. /
        ind_random = rnd.randint(0, len(texto)-1)
    
        if memory.running_mode == "terminal":
            # Rodando no modo terminal....
            print('[b white]State:[/] The Robot is [b blue]speaking[/] the sentence: [b white]"[/]', end="")
            for c in texto[ind_random]:
                print('[b white]' + c + '[/]', end="")
                time.sleep(0.08)
            print('[b white]"')


        elif memory.running_mode == "terminal-plus":
            global voice_type, auth_start_time, apikey, url, authenticator, tts, first_requisition
            # Assumes the default UTF-8 (Generates the hashing of the audio file).
            # Additionally, use the voice timbre attribute in the file hash.
            if xml_node.get("voiceType") == None:
                voice_type = memory.default_voice
            else:
                voice_type = xml_node.get('voiceType')


            texto[ind_random] = texto[ind_random].lower()
            hash_object = hashlib.md5(texto[ind_random].encode())
            file_name = "_audio_"  + voice_type + hash_object.hexdigest()
            audio_file_is_ok = False
            while(not audio_file_is_ok):
                # Checks if the speech audio already exists in the cache folder.
                if not (os.path.isfile("robot_package/talk_module/tts_cache_files/" + file_name + config.WATSON_AUDIO_EXTENSION)): # If it doesn't exist, call Watson.
                    '[b white]State:[/] The Robot is [b blue]speaking[/] the sentence: [b white]"' + texto[ind_random] + '[/]"'
                    print("[b white]State:[/][b yellow] The file is not cached... Let's try to generate it![/]")

                    # Tests with the first request after a module reset (There is no problem in this way).
                    # ================================================== ======================================
                    # Watson appears to impose a limited connection time from the first request.
                    # 1min of inactivity -> OK
                    # 2min of inactivity -> OK
                    # 8min of inactivity -> OK

                    # Tests with one request from another, without resetting the module.
                    # ================================================== ======================================
                    # 3min of inactivity from the first request -> OK
                    # 3.30min of inactivity from the first request -> OK
                    # 4min of inactivity from a first req. -> Crashed! (Request rejected)
                    # 5min of inactivity from the first request.-> Crashed! (Request rejected)

                    # Checks if the module has been inactive for more than 3min (180s) since the first request.
                    # print(first_requisition, (time.time() - auth_start_time))
                    if (not(first_requisition) and (time.time() - auth_start_time >= 180)):
                        print("The module has been inactive for more than 3 minutes (since the first request) and a new authentication will be performed.")
                        # Watson API key (config.)
                        with open("robot_package/talk_module/ibm_cred.txt", "r") as ibm_cred: 
                            ibm_config = ibm_cred.read().splitlines()
                        apikey = ibm_config[0]
                        url = ibm_config[1]
                        # Setup Watson service
                        authenticator = IAMAuthenticator(apikey)
                        # TTS service
                        tts = TextToSpeechV1(authenticator = authenticator)
                        tts.set_service_url(url)
                        first_requisition = False
                        auth_start_time = time.time() # Momento da autenticação.

                    # Start the TTS process
                    tts_start = time.time() # Variable used to mark the processing time of the TTS service.
                    while(not audio_file_is_ok):
                        # Functions of the TTS service for EVA
                        with open("robot_package/talk_module/tts_cache_files/" + file_name + config.WATSON_AUDIO_EXTENSION, 'wb') as audio_file:
                            try:
                                res = tts.synthesize(texto[ind_random], accept = config.ACCEPT_AUDIO_EXTENSION, voice = voice_type).get_result()
                                print("[b white]State:[/][b green] Writing content to cache...[/]")
                                audio_file.write(res.content)
                                file_size = os.path.getsize("robot_package/talk_module/tts_cache_files/" + file_name + config.WATSON_AUDIO_EXTENSION)
                                if file_size == 0: # Corrupted file!
                                    print("#### Corrupted file....")
                                    os.remove("robot_package/talk_module/tts_cache_files/" + file_name + config.WATSON_AUDIO_EXTENSION)
                                else:
                                    try:
                                        print('[b white]State:[/] The Robot is [b blue]speaking[/] the sentence: [b white]"' + texto[ind_random] + '[/]"')
                                        playsound("robot_package/talk_module/tts_cache_files/" + file_name + ".mp3", block = True)
                                    except FileNotFoundError as e:
                                        print('[b white on red blink] FATAL ERROR [/]: [b yellow reverse] There was a problem playing the audio file [/]: [b white]"' + xml_node.get("source") + '"[/]. Check if it [b u white]exists[/] or is in the [b u white]correct format[/] (wav)[/].✋⛔️')
                                        exit(1) 

                                    audio_file_is_ok = True
                                    first_requisition = False
                            except ApiException as ex:
                                print ("The function failed with the following error code: " + str(ex.code) + ": " + ex.message)
                                exit(1)
                else:
                    if (os.path.getsize("robot_package/talk_module/tts_cache_files/" + file_name + config.WATSON_AUDIO_EXTENSION)) == 0: # Corrupted file
                        # The generated audio file is 0 bytes, corrupt and will be removed!
                        os.remove("robot_package/talk_module/tts_cache_files/" + file_name + config.WATSON_AUDIO_EXTENSION)
                    else:
                        # The file is more than 0 bytes and will be played now!
                        try:
                            print('[b white]State:[/] The Robot is [b blue]speaking[/] the sentence: [b white]"' + texto[ind_random] + '"[/]')
                            playsound("robot_package/talk_module/tts_cache_files/" + file_name + ".mp3", block = True)
                        except FileNotFoundError as e:
                            print('[b white on red blink] FATAL ERROR [/]: [b yellow reverse] There was a problem playing the audio file [/]: [b white]"' + xml_node.get("source") + '"[/]. Check if it [b u white]exists[/] or is in the [b u white]correct format[/] (wav)[/].✋⛔️')
                            exit(1) 
                        audio_file_is_ok = True  

        else:
            # Controls the physical robot
            print('[b white]State:[/] The Robot is [b blue]speaking[/] the sentence: [b white]"' + texto[ind_random] + '"[/]')

            if xml_node.get("voiceType") == None:
                message = memory.default_voice + "|" + memory.default_voice_pitch_shift + "|" + texto[ind_random]
            else:
                message = xml_node.get("voiceType") + "|" + xml_node.get("pitchShift") + "|" + texto[ind_random]
            
            # client_mqtt.publish(topic_base + '/' + xml_node.tag, message)
            
            # block("Speaking", memory, client_mqtt)

        return xml_node # It returns the same node
