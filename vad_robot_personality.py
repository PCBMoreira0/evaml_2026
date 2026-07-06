import tkinter as tk
from tkinter import messagebox
import paho.mqtt.client as mqtt

# --- CONFIGURAÇÃO MQTT ---
MQTT_BROKER = "localhost"  # Altere para o IP da máquina onde roda o ROSE/SENSEI
MQTT_PORT = 1883
MQTT_TOPIC = "SIMULATOR/ROBOT_PERSONALITY"

class VAParametersApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ROSE - Robot Sentiment Engine)")
        # Mantendo o padrão de tamanho e proporção de janelas anteriores (+50%)
        self.root.geometry("600x700")
        self.root.resizable(False, False)
        
        # Conexão MQTT
        self.mqtt_client = mqtt.Client()
        try:
            self.mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
            self.mqtt_client.loop_start()
        except Exception as e:
            print(f"[Aviso] Não foi possível conectar ao broker MQTT: {e}")
            
        self.setup_ui()

    def setup_ui(self):
        # Header Principal
        header_label = tk.Label(
            self.root, 
            text="Configuração dos Parâmetros da Personalidade do Robô", 
            font=("Arial", 16, "bold"), 
            fg="#1e293b"
        )
        header_label.pack(pady=20)
        
        # --- CONTAINER 1: DECAY EMOCIONAL ---
        decay_frame = tk.LabelFrame(self.root, text=" 1. Decay Emocional ", padx=15, pady=10, font=("Arial", 11, "bold"))
        decay_frame.pack(fill="x", padx=30, pady=10)
        
        decay_desc = tk.Label(decay_frame, text="Define a velocidade com que o robô retorna ao estado neutro (1-D).", font=("Arial", 9, "italic"), fg="#64748b")
        decay_desc.pack(anchor="w", pady=2)
        
        # Slider de 0.00 a 1.00
        self.scale_decay = tk.Scale(decay_frame, from_=0.0, to=1.0, resolution=0.01, orient="horizontal", font=("Arial", 11), length=450)
        self.scale_decay.set(0.05)  # Valor padrão típico
        self.scale_decay.pack(pady=5)
        
        # --- CONTAINER 2: FATOR EMPÁTICO ---
        empathy_frame = tk.LabelFrame(self.root, text=" 2. Fator Empático (Sensibilidade ao Vetor Afetivo do Usuário) ", padx=15, pady=10, font=("Arial", 11, "bold"))
        empathy_frame.pack(fill="x", padx=30, pady=10)
        
        empathy_desc = tk.Label(empathy_frame, text="Peso de influência do vetor de emoção do usuário no cálculo do ROSE.", font=("Arial", 9, "italic"), fg="#64748b")
        empathy_desc.pack(anchor="w", pady=2)
        
        # Slider de 0.00 a 1.00
        self.scale_empathy = tk.Scale(empathy_frame, from_=0.0, to=1.0, resolution=0.01, orient="horizontal", font=("Arial", 11), length=450)
        self.scale_empathy.set(0.40)  # Valor padrão típico
        self.scale_empathy.pack(pady=5)
        
        # --- CONTAINER 3: BASE MOOD (Eixos V e A) ---
        mood_frame = tk.LabelFrame(self.root, text=" 3. Base Mood (Humor Base do Robô) ", padx=15, pady=10, font=("Arial", 11, "bold"))
        mood_frame.pack(fill="x", padx=30, pady=10)
        
        mood_desc = tk.Label(mood_frame, text="Humor fixo do robô (ponto de equilíbrio fora de estímulos).", font=("Arial", 9, "italic"), fg="#64748b")
        mood_desc.pack(anchor="w", pady=5)
        
        # Sub-widgets para Valence e Arousal do Mood
        v_label = tk.Label(mood_frame, text="Valência do Mood:", font=("Arial", 10, "bold"))
        v_label.pack(anchor="w")
        self.scale_mood_v = tk.Scale(mood_frame, from_=-1.0, to=1.0, resolution=0.05, orient="horizontal", font=("Arial", 10), length=450)
        self.scale_mood_v.set(0.0)
        self.scale_mood_v.pack(pady=2)
        
        a_label = tk.Label(mood_frame, text="Arousal do Mood:", font=("Arial", 10, "bold"))
        a_label.pack(anchor="w")
        self.scale_mood_a = tk.Scale(mood_frame, from_=-1.0, to=1.0, resolution=0.05, orient="horizontal", font=("Arial", 10), length=450)
        self.scale_mood_a.set(0.0)
        self.scale_mood_a.pack(pady=2)
        
        # --- BOTÃO DE ENVIO ---
        self.status_label = tk.Label(self.root, text="Pronto para enviar", font=("Arial", 11, "bold"), fg="#475569")
        self.status_label.pack(pady=10)
        
        send_btn = tk.Button(
            self.root, 
            text="Enviar Parâmetros de Perfil por MQTT", 
            bg="#2563EB", 
            fg="white", 
            font=("Arial", 14, "bold"), 
            height=2, 
            command=self.send_parameters
        )
        send_btn.pack(fill="x", padx=30, pady=5)

    def send_parameters(self):
        # Coleta os valores atuais lidos dos Sliders
        decay = self.scale_decay.get()
        empathy = self.scale_empathy.get()
        mood_v = self.scale_mood_v.get()
        mood_a = self.scale_mood_a.get()
        
        # Monta a string de payload estruturada (ex: "0.05,0.40,0.00,0.00")
        # payload = f"{decay:.2f},{empathy:.2f},{mood_v:.2f},{mood_a:.2f}"
        payload = "perfil" + "|" + str(empathy) + "|" + str(decay) + "|"  + str(mood_v) + "," + str(mood_a) + ",0.00" # Por ultimo um valor zerado para dominancia
        print(payload)
        
        try:
            result = self.mqtt_client.publish(MQTT_TOPIC, payload, qos=1)
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                print(f"[MQTT] Parâmetros publicados em {MQTT_TOPIC}: {payload}")
                
                # Feedback visual rápido de sucesso na interface
                self.status_label.config(text="✓ Parâmetros atualizados no ROSE!", fg="#16a34a")
                self.root.after(1500, lambda: self.status_label.config(text="Pronto para enviar", fg="#475569"))
            else:
                raise Exception("Código de retorno inválido do Broker.")
        except Exception as e:
            messagebox.showerror("Erro MQTT", f"Falha ao enviar parâmetros: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = VAParametersApp(root)
    root.mainloop()