import config # Module with network device configurations.

import time
import random as rnd
import hashlib
import os


from rich import print


class TtsIBM():

    def __init__(self, xml_node):

        self.xml_node = xml_node
        # Watson imports
        from ibm_watson import TextToSpeechV1
        from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
        from ibm_watson import ApiException
        

        # Watson API configuration key.
        with open("robot_package/talk_module/ibm_cred.txt", "r") as ibm_cred: 
            ibm_config = ibm_cred.read().splitlines()
        apikey = ibm_config[0]
        url = ibm_config[1]

        # Setup Watson service.
        authenticator = IAMAuthenticator(apikey)

        # TTS service.
        self.tts = TextToSpeechV1(authenticator = authenticator)
        self.tts.set_service_url(url)

        self.auth_start_time = time.time() # Time of authentication.
        self.first_requisition = True; # Indicates that this is the first request for the Watson service.

    def make_tts_and_play(self, text_to_speech, voice_type):

        text_to_speech = text_to_speech.lower()
        hash_object = hashlib.md5(text_to_speech.encode())
        file_name = "_audio_"  + voice_type + hash_object.hexdigest()
        audio_file_is_ok = False
        while(not audio_file_is_ok):
            # Checks if the speech audio already exists in the cache folder.
            if not (os.path.isfile("robot_package/talk_module/tts_cache_files/" + file_name + config.WATSON_AUDIO_EXTENSION)): # If it doesn't exist, call Watson.
                '[b white]State:[/] The Robot is [b blue]speaking[/] the sentence: [b white]"' + text_to_speech + '[/]"'
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
                if (not(self.first_requisition) and (time.time() - self.auth_start_time >= 180)):
                    print("The module has been inactive for more than 3 minutes (since the first request) and a new authentication will be performed.")
                    # Watson API key (config.)
                    with open("robot_package/talk_module/ibm_cred.txt", "r") as ibm_cred: 
                        ibm_config = ibm_cred.read().splitlines()
                    apikey = ibm_config[0]
                    url = ibm_config[1]
                    # Setup Watson service
                    authenticator = self.IAMAuthenticator(apikey)
                    # TTS service
                    self.tts = self.TextToSpeechV1(authenticator = authenticator)
                    self.tts.set_service_url(url)
                    self.first_requisition = False
                    self.auth_start_time = time.time() # Momento da autenticação.

                # Start the TTS process
                tts_start = time.time() # Variable used to mark the processing time of the TTS service.
                while(not audio_file_is_ok):
                    # Functions of the TTS service
                    with open("robot_package/talk_module/tts_cache_files/" + file_name + config.WATSON_AUDIO_EXTENSION, 'wb') as audio_file:
                        try:
                            res = self.tts.synthesize(text_to_speech, accept = config.ACCEPT_AUDIO_EXTENSION, voice = voice_type).get_result()
                            print("[b white]State:[/][b green] Writing content to cache...[/]")
                            audio_file.write(res.content)
                            file_size = os.path.getsize("robot_package/talk_module/tts_cache_files/" + file_name + config.WATSON_AUDIO_EXTENSION)
                            if file_size == 0: # Corrupted file!
                                print("#### Corrupted file....")
                                os.remove("robot_package/talk_module/tts_cache_files/" + file_name + config.WATSON_AUDIO_EXTENSION)
                            else:
                                audio_file_is_ok = True
                                self.first_requisition = False
                                return file_name # The new audio file was generated and is ready to play.
                                # try:
                                #     print('[b white]State:[/] The Robot is [b blue]speaking[/] the sentence: [b white]"' + text_to_speech + '[/]"')
                                #     playsound("robot_package/talk_module/tts_cache_files/" + file_name + ".mp3", block = True)
                                # except FileNotFoundError as e:
                                #     print('[b white on red blink] FATAL ERROR [/]: [b yellow reverse] There was a problem playing the audio file [/]: [b white]"' + xml_node.get("source") + '"[/]. Check if it [b u white]exists[/] or is in the [b u white]correct format[/] (wav)[/].✋⛔️')
                                #     exit(1) 

                                # audio_file_is_ok = True
                                # self.first_requisition = False
                        except self.ApiException as ex:
                            print ("The function failed with the following error code: " + str(ex.code) + ": " + ex.message)
                            return False
            else:
                if (os.path.getsize("robot_package/talk_module/tts_cache_files/" + file_name + config.WATSON_AUDIO_EXTENSION)) == 0: # Corrupted file
                    # The generated audio file is 0 bytes, corrupt and will be removed!
                    os.removeaudio_file_is_ok = True
                    # self.first_requisition = False("robot_package/talk_module/tts_cache_files/" + file_name + config.WATSON_AUDIO_EXTENSION)
                else:
                    # The file is more than 0 bytes and will be played now!
                    # try:
                    #     print('[b white]State:[/] The Robot is [b blue]speaking[/] the sentence: [b white]"' + text_to_speech + '"[/]')
                    #     playsound("robot_package/talk_module/tts_cache_files/" + file_name + ".mp3", block = True)
                    # except FileNotFoundError as e:
                    #     print('[b white on red blink] FATAL ERROR [/]: [b yellow reverse] There was a problem playing the audio file [/]: [b white]"' + self.xml_node.get("source") + '"[/]. Check if it [b u white]exists[/] or is in the [b u white]correct format[/] (wav)[/].✋⛔️')
                    #     exit(1) 
                    audio_file_is_ok = True
                    return file_name
