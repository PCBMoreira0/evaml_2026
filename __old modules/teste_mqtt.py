import paho.mqtt.client as mqtt
import time

# 1. Configurações
BROKER = "192.168.0.28"
PORT = 1883
TOPIC = "teste"
MENSAGEM = "Olá, mundo!"

# # 2. Criação do cliente
# client = mqtt.Client()

# # 3. Conexão ao broker
# print(f"Conectando ao broker em '{BROKER}'...")
# client.connect(BROKER, PORT, 60)

# # 4. Inicia o loop para processar a rede (não bloqueia)
# # É fundamental para que a mensagem seja realmente enviada
# client.loop_start()

# # 5. Publica a mensagem
# print(f"Publicando a mensagem: '{MENSAGEM}' no tópico '{TOPIC}'")
# client.publish(TOPIC, MENSAGEM)

# # Dá um tempo para a mensagem ser enviada
# time.sleep(1) 

# # 6. Desconecta o cliente
# print("Desconectando o cliente.")
# client.loop_stop()
# client.disconnect()

# 2. Callback para a conexão
def on_connect(client, userdata, flags, rc):
    print("Conectado ao broker! Assinando o tópico...")
    # A assinatura é feita aqui para garantir resiliência
    client.subscribe("teste")

# 3. Callback para o recebimento de mensagens
def on_message(client, userdata, msg):
    print(f"Mensagem recebida: Tópico '{msg.topic}' | Mensagem '{msg.payload.decode()}'")

# 4. Criação e configuração do cliente
client = mqtt.Client()
# client.on_connect = on_connect
client.on_message = on_message

# 5. Conexão ao broker
client.connect(BROKER, PORT, 60)

# 6. Inicia o loop de escuta (bloqueia o programa)
# O loop_forever() mantém o programa rodando e aguardando mensagens.

time.sleep(3)
client.on_connect = on_connect
print("Pode enviar...")
# client.subscribe("teste")

try:
    print("Aguardando mensagens... (Pressione Ctrl+C para sair)")
    # client.loop_forever()
    client.loop_start()
    while 1:
        print("oi")
        time.sleep(2)

except KeyboardInterrupt:
    print("\nPrograma encerrado pelo usuário.")

finally:
    # Desconecta o cliente de forma limpa
    client.disconnect()