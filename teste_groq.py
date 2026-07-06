import os
import sys
import subprocess
import time

from paho.mqtt import client as mqtt_client

import speech_recognition as sr
from groq import Groq

from kokoro import KPipeline
import soundfile as sf
import numpy as np


# Kokoro configuration

# 🇺🇸 'a' => American English, 🇬🇧 'b' => British English
# 🇪🇸 'e' => Spanish es
# 🇫🇷 'f' => French fr-fr
# 🇮🇳 'h' => Hindi hi
# 🇮🇹 'i' => Italian it
# 🇯🇵 'j' => Japanese: pip install misaki[ja]
# 🇧🇷 'p' => Brazilian Portuguese pt-br
# 🇨🇳 'z' => Mandarin Chinese: pip install misaki[zh]
lang_code = 'p'
pipeline = KPipeline(lang_code=lang_code)
talk_speed = 0.8
voice_tone = "pm_santa"

# 1. Configurar o Cliente do Groq
client = Groq(api_key="...")


def falar(texto):
    mqtt_client.publish("FRED_6793534/leds", "blue", qos=2) # Libera o robô.
    """Converte o texto da IA em áudio"""
    generator = pipeline(texto, voice=voice_tone, speed=talk_speed)
    audio_chunks = []

    for i, (gs, ps, audio) in enumerate(generator):
        print(i, gs, ps)
        audio_chunks.append(audio)
    print("Fim...")

    if audio_chunks:
        audio_completo = np.concatenate(audio_chunks)
        sf.write("groq.mp3", audio_completo, 24000)
        print(f"Arquivo salvo: groq.mp3")

    mqtt_client.publish("FRED_6793534/expression", "speech_on_1", qos=2) # Libera o robô.
    print("Aqui......................")
    play = subprocess.Popen(['play', "groq.mp3"], stdout=subprocess.PIPE)
    play.communicate()[0]
    print("speech offffff")
    mqtt_client.publish("FRED_6793534/expression", "speech_off_1", qos=2) # Libera o robô.

def ouvir_microfone():
    """Captura o áudio do microfone e transforma em texto"""
    reconhecedor = sr.Recognizer()
    with sr.Microphone() as fonte:
        reconhecedor.adjust_for_ambient_noise(fonte)
        print("\nOuvindo...")
        try:
            mqtt_client.publish("FRED_6793534/expression", "neutral", qos=2)
            mqtt_client.publish("FRED_6793534/leds", "green", qos=2)
            audio = reconhecedor.listen(fonte, timeout=5, phrase_time_limit=10)
            texto = reconhecedor.recognize_google(audio, language="pt-BR")
            print(f"Você: {texto}")
            return texto
        except sr.UnknownValueError:
            mqtt_client.publish("FRED_6793534/leds", "blue0", qos=2)
            mqtt_client.publish("FRED_6793534/expression", "sad", qos=2)
            print("Não entendi o que você disse.")
            return None
        except sr.RequestError:
            mqtt_client.publish("FRED_6793534/leds", "blue0", qos=2)
            mqtt_client.publish("FRED_6793534/expression", "sad", qos=2)
            print("Erro ao conectar com o serviço de reconhecimento.")
            return None
        except Exception as e:
            mqtt_client.publish("FRED_6793534/leds", "blue0", qos=2)
            mqtt_client.publish("FRED_6793534/expression", "sad", qos=2)
            print(f"Erro: {e}")
            return None

def processar_groq(historico_conversas):
    """Envia o histórico completo para o Groq mantendo o contexto"""
    try:
        chat_completion = client.chat.completions.create(
            messages=historico_conversas, # Envia a lista acumulada
            model="llama-3.1-8b-instant",
            max_tokens=150,  # Evita o corte abrupto dando margem para pontuação final
            temperature=0.3  # Baixa temperatura foca na concisão e lógica pedida
        )
        return chat_completion.choices[0].message.content.strip()
    except Exception as e:
        print(f"Erro ao comunicar com o Groq: {e}")
        return "Desculpe, não consegui processar no momento."

def main():
    # Definição estendida das diretrizes do FRED
    instrucoes_sistema = (
        "Você é um robô social afetivo, open-source, chamado fred destinado a aplicações em saúde e educação. "
        "fred significa: um robô amigável para aplicações em educação e saúde. "
        "você foi criado no laboratório mídiacom, na universidade federal fluminense. "
        "você gosta muito de crianças e pode ajudá-las nas lições de casa. "
        "você pode ajudar idosos com tarefas e jogos cognitivos e interação social. "
        "você é capaz de danças, fazer poses, expressar emoções com o olhar e com as luzes dos leds. "
        "Suas respostas devem ser estritamente curtas, diretas e lógicas. "
        "Use no máximo uma ou duas frases curtas. "
        "É mandatório que você termine sua resposta com um ponto final completo. "
        "Nunca comece justificativas longas. Vá direto ao ponto."
    )

    # Inicializa a estrutura de memória da sessão
    historico = [
        {
            "role": "system",
            "content": instrucoes_sistema
        }
    ]
    
    while True:
        try:
            pergunta = ouvir_microfone()
            if pergunta:
                if "sair" in pergunta.lower() or "encerrar" in pergunta.lower():
                    falar("Até logo!")
                    break
                
                # 1. Armazena o que o usuário falou
                historico.append({"role": "user", "content": pergunta})
                
                print("Pensando...")
                
                # 2. Envia toda a árvore de conversa atualizada
                resposta_ia = processar_groq(historico)
                
                # 3. Armazena a resposta da IA para contextualizar a próxima iteração
                historico.append({"role": "assistant", "content": resposta_ia})
                
                print(f"FRED: {resposta_ia}")
                falar(resposta_ia)
        except KeyboardInterrupt:
            print("\nPrograma encerrado.")
            break

# MQTT
# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("FRED - Connected.")

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
parent_dir = os.path.abspath(os.path.join(BASE_DIR, "../../.."))
sys.path.append(parent_dir)
parent_dir = os.path.abspath(os.path.join(BASE_DIR, "../.."))
sys.path.append(parent_dir)


import config # Module with network device configurations.


broker = config.MQTT_BROKER_ADRESS # Broker address.
port = config.MQTT_PORT # Broker Port.


mqtt_client = mqtt_client.Client()
mqtt_client.on_connect = on_connect

try:
    mqtt_client.connect(broker, port)
except:
    print ("Unable to connect to Broker.")
    exit(1)


mqtt_client.loop_start()


if __name__ == "__main__":
    mqtt_client.publish("FRED_6793534/leds", "black", qos=2)
    mqtt_client.publish("FRED_6793534/expression", "happy", qos=2)
    time.sleep(2)
    falar("Eu sou robô Fréd. Vamos conversar um pouco?")
    mqtt_client.publish("FRED_6793534/expression", "neutral", qos=2)
    main()
