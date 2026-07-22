import os
import sys



import tkinter as tk
from tkinter import ttk
import threading
import paho.mqtt.client as mqtt
from transformers import pipeline


print("Carregando o modelo de IA (Emotion Classifier)... Aguarde.")
# MUDANÇA AQUI: top_k=None faz o modelo retornar TODAS as emoções calculadas
classifier = pipeline("sentiment-analysis", model="michellejieli/emotion_text_classifier", top_k=None)
print("Modelo carregado com sucesso!")

class EmotionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Analisador de Emoções via MQTT")
        self.root.geometry("550x450")
        self.root.configure(bg="#f0f2f5")

        style = ttk.Style()
        style.configure("TLabel", background="#f0f2f5", font=("Helvetica", 11))
        style.configure("Header.TLabel", font=("Helvetica", 14, "bold"))

        # Título
        self.lbl_titulo = ttk.Label(root, text="Monitor de Emoções Completo", style="Header.TLabel")
        self.lbl_titulo.pack(pady=15)

        # Seção: Texto Recebido
        self.lbl_txt_titulo = ttk.Label(root, text="Último Texto Recebido:", font=("Helvetica", 10, "bold"))
        self.lbl_txt_titulo.pack(anchor="w", padx=20)
        
        self.txt_mensagem = tk.Text(root, height=3, width=60, wrap="word", font=("Helvetica", 10))
        self.txt_mensagem.pack(pady=5, padx=20)
        self.txt_mensagem.insert("1.0", "Aguardando primeira mensagem do MQTT...")
        self.txt_mensagem.config(state="disabled")

        ttk.Separator(root, orient="horizontal").pack(fill="x", padx=20, pady=15)

        # Seção: Probabilidades de Todas as Emoções
        self.lbl_resultado_titulo = ttk.Label(root, text="Probabilidades das Emoções:", font=("Helvetica", 10, "bold"))
        self.lbl_resultado_titulo.pack(anchor="w", padx=20)

        # Usaremos um widget Text estilizado para exibir a lista formatada de emoções
        self.txt_probabilidades = tk.Text(root, height=8, width=60, wrap="word", font=("Courier", 11), bg="#ffffff")
        self.txt_probabilidades.pack(pady=10, padx=20)
        self.txt_probabilidades.insert("1.0", "Nenhum dado processado ainda.")
        self.txt_probabilidades.config(state="disabled")

        self.start_mqtt_thread()

    def atualizar_interface(self, texto, lista_emocoes):
        """Atualiza a interface com o texto e o ranking completo de emoções"""
        # 1. Atualiza o texto recebido
        self.txt_mensagem.config(state="normal")
        self.txt_mensagem.delete("1.0", tk.END)
        self.txt_mensagem.insert("1.0", texto)
        self.txt_mensagem.config(state="disabled")

        # 2. Monta o texto com a lista de probabilidades
        texto_ranking = ""
        # 'lista_emocoes' agora é algo como: [{'label': 'joy', 'score': 0.85}, {'label': 'surprise', 'score': 0.10}, ...]
        for item in lista_emocoes:
            emocao = item['label'].upper().ljust(12)  # Alinha o texto à esquerda
            if emocao == "JOY         ": emocao = "HAPPINESS   "
            barra_progresso = "■" * int(item['score'] * 20)  # Cria uma barrinha visual simples
            porcentagem = f"{item['score'] * 100:6.2f}%"
            
            texto_ranking += f"{emocao} : {porcentagem} {barra_progresso}\n"

        # 3. Atualiza o campo de probabilidades
        self.txt_probabilidades.config(state="normal")
        self.txt_probabilidades.delete("1.0", tk.END)
        self.txt_probabilidades.insert("1.0", texto_ranking)
        self.txt_probabilidades.config(state="disabled")

    def processar_mensagem(self, texto_recebido):
        try:
            resultado = classifier(texto_recebido)
            
            # Se a resposta vier aninhada como [[{...}]], removemos a camada extra
            if isinstance(resultado[0], list):
                lista_emocoes = resultado[0]
            else:
                lista_emocoes = resultado

            # lista_emocoes agora contém todos os dicionários ordenados por relevância
            self.root.after(0, self.atualizar_interface, texto_recebido, lista_emocoes)
        except Exception as e:
            print(f"Erro ao processar IA: {e}")

    def on_message(self, client, userdata, msg):
        try:
            texto = msg.payload.decode("utf-8")
            threading.Thread(target=self.processar_mensagem, args=(texto,), daemon=True).start()
        except Exception as e:
            print(f"Erro ao decodificar mensagem: {e}")

    def start_mqtt_thread(self):
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        client.on_connect = lambda c, u, f, rc, props=None: c.subscribe(TOPIC)
        client.on_message = self.on_message
        try:
            client.connect(BROKER, PORT, 60)
            client.loop_start()
        except Exception as e:
            print(f"Erro no MQTT: {e}")



if __name__ == "__main__":
    BROKER = "127.0.0.1"
    PORT = 1883
    TOPIC = "SIMULATOR/TER_TEXT"

    root = tk.Tk()
    app = EmotionApp(root)
    root.mainloop()