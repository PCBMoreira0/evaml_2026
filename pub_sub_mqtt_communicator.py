import paho.mqtt.client as mqtt
import queue
from communicator_interface import CommunicatorInterface # Supondo a interface em um arquivo separado

import config

import robot_package.robot_profile as robot_profile


class ResponseTimeout(TimeoutError):
    """O robô não respondeu dentro do tempo limite."""

class ResponseCancelled(Exception):
    """A espera pela resposta foi interrompida pelo usuário (ver cancel())."""

_CANCEL = object() # Marca colocada na fila por cancel() para acordar o receive().

# 
class PubSubMqttComunicator(CommunicatorInterface):
    def __init__(self, node_xml):

        # Criação do cliente Paho MQTT
        self.client = mqtt.Client()
        
        # Definição das callbacks de conexão e mensagem
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        
        # Conexão e início do loop
        self.client.connect(config.MQTT_BROKER_ADRESS, config.MQTT_PORT, 60)
        
        self.pub_topic = node_xml.get("pubTopic")
        self.sub_topic = node_xml.get("subTopic")
        self.response_queue = queue.Queue()
        self.timeout = config.MQTT_RESPONSE_TIMEOUTS.get(self.sub_topic, config.MQTT_RESPONSE_TIMEOUT)
        self.client.loop_start()
        print(f"Sync MQTT: Configurado. Tópicos req:'{self.pub_topic}', resp:'{self.sub_topic }'")


    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Sync MQTT: Conectado. Assinando tópicos de resposta...")
            # A assinatura é crucial para a reconexão
            print("Subscribed:", robot_profile.ROBOT_BASE_TOPIC + "/" + self.sub_topic)
            client.subscribe(robot_profile.ROBOT_BASE_TOPIC + "/" + self.sub_topic)
        else:
            print(f"Sync MQTT: Falha na conexão com código {rc}.")
    

    def _on_message(self, client, userdata, msg):
        # Colocando a mensagem recebida na fila para processamento síncrono
        print(f"Sync MQTT: Mensagem recebida de '{msg.topic}', colocando na fila.")
        self.response_queue.put(msg.payload.decode())


    def send(self, **kwargs):
        # Lógica de envio
        self.topic_base = ""

        if "mqtt_message" in kwargs:

            message = kwargs["mqtt_message"]
        else:
            message = "SERVICE_REQUEST"

        if "topic_base" in kwargs:
            self.topic_base = kwargs["topic_base"] + "/"
        pub_topic = kwargs.get("pub_topic", self.pub_topic)
        if pub_topic == self.pub_topic:
            # Nova requisição: descarta respostas antigas que ainda estejam na fila,
            # para que o receive() espere pela resposta DESTA requisição.
            self._discard_stale_responses()
        self.client.publish(self.topic_base + pub_topic, message)

        print(f"OneWay MQTT: Enviando comando unidirecional -> {message}")

    def _discard_stale_responses(self):
        while True:
            try:
                stale = self.response_queue.get_nowait()
            except queue.Empty:
                return
            if stale is not _CANCEL:
                print(f"Sync MQTT: Descartando resposta antiga -> {stale}")

    def cancel(self):
        """Interrompe um receive() em andamento (chamado de outra thread)."""
        self.response_queue.put(_CANCEL)

    def receive(self) -> dict:
        # Lógica de recebimento síncrono (bloqueia)
        print(f"Sync MQTT: Bloqueando e aguardando resposta em '{self.sub_topic}' (limite: {self.timeout}s)...")
        try:
            response = self.response_queue.get(timeout=self.timeout)
        except queue.Empty:
            # Uma resposta que chegue depois disto é descartada no próximo send().
            raise ResponseTimeout(f"O robô não respondeu em '{self.sub_topic}' após {self.timeout}s.") from None
        if response is _CANCEL:
            raise ResponseCancelled(f"Espera por '{self.sub_topic}' interrompida pelo usuário.")
        print(f"Sync MQTT: Resposta recebida -> {response}")
        return {"RESPONSE": response}