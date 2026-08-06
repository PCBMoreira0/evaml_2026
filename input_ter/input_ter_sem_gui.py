import os
import sys

import json

from paho.mqtt import client as mqtt_client

from transformers import pipeline

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
parent_dir = os.path.abspath(os.path.join(BASE_DIR, "../"))
sys.path.append(parent_dir)


import config  # Module with network device configurations.

sys.path.append(os.getcwd() + "/" + "robot_package/")

import robot_profile


broker = config.MQTT_BROKER_ADRESS # Broker address.
port = config.MQTT_PORT # Broker Port.

robot_base_topic = robot_profile.ROBOT_BASE_TOPIC


print("Carregando o modelo de IA (Emotion Classifier)... Aguarde.")
# MUDANÇA AQUI: top_k=None faz o modelo retornar TODAS as emoções calculadas
classifier = pipeline("sentiment-analysis", model="michellejieli/emotion_text_classifier", top_k=None)
print("Modelo 'michellejieli/emotion_text_classifier' carregado com sucesso!")

result_to_pulse = json.dumps({})
list_sources_to_receive = []

# MQTT
# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    # Subscribing in on_connect() means that if we lose the connection and
    # Reconnect then subscriptions will be renewed.
    # client.subscribe(topic=[(sim_base_topic + '/PERCEPTION', 1), ]) # Simulator topic
    client.subscribe(topic=[(robot_base_topic + "/" + 'PERCEPTION', 1), ]) # Robot topic
    # client.subscribe(topic=[(sim_base_topic + '/TER_TEXT', 1), ]) # Simulator topic
    client.subscribe(topic=[(robot_base_topic + "/" + 'TER_TEXT', 1), ]) # Robot topic
    print("Text Emotion Recognition (TER) - Input Module - Connected.", robot_base_topic + '/TER_TEXT')
         

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    global result_to_pulse, list_sources_to_receive

    # Recebe a definição das fontes usadas na janela de percepção
    if msg.topic == robot_base_topic + '/PERCEPTION':
    
        message = json.loads(msg.payload.decode()) # Transforma a mensagem para JSON

        # Padrão das duas mensagens (START e END) do tópico PERCEPTION
        # {"action": "START", "sources": ["FER", "TER"]}
        # {"action": "END"}

        if message["action"] == "START": # A mensagem de END não interessa ao PULSE porque ele finaliza após a recepção de todos os sources 
            list_sources_to_receive = message["sources"]
            print("Lista de fontes:", list_sources_to_receive)

        # Se action igual END, envia o resultado da classificação, já formatado, para o PULSE
        else:
            print("list...", list_sources_to_receive)
            if "TER" in list_sources_to_receive:
                print("é um end.... e é um ter")
                client.publish(robot_base_topic + "/PULSE/INPUT", result_to_pulse)
                print("Zerando a lista....")
                list_sources_to_receive = []


    if msg.topic == robot_base_topic + "/" + 'TER_TEXT':
        # Precisamos classificar o texto da mensagem e montar o JSON que será enviado para o PULSE
        resultado = classifier(msg.payload.decode())[0] # Uma lista com 7 dicionários, cada um conteno "label" e "score".
        
        # Formatação de saída
        
        # {
        #     "source": "TER",
        #     "representation": "CAT",
        #     "probabilities": {
        #         "happy": 0.05,
        #         "sad": 0.10,
        #         "angry": 0.70,
        #         "surprise": 0.05,
        #         "neutral": 0.10
        #     }
        # }

        aux = {}
        for i in range(len(resultado)):
            if resultado[i]["label"] == "joy":
                resultado[i]["label"] = "happiness"

            aux[resultado[i]['label']] = resultado[i]['score']

        
        result_to_pulse = {
            "source": "TER",
            "representation": "CAT",
            "probabilities": aux
        }

        # Transforma para JSON
        result_to_pulse = json.dumps(result_to_pulse)
        print(result_to_pulse)
       


# Run the MQTT client thread.
client = mqtt_client.Client()
client.on_connect = on_connect
client.on_message = on_message
try:
    client.connect(broker, port)
except:
    print ("Unable to connect to Broker.")
    exit(1)

# You cannot use the "forever" method (as in other modules) because it blocks not allowing
# for the graphical interface thread loop to execute.
# client.loop_forever()

client.loop_forever()