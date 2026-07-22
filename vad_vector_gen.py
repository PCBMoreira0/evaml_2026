import tkinter as tk
from tkinter import messagebox
import paho.mqtt.client as mqtt

# --- CONFIGURAÇÃO MQTT ---
MQTT_BROKER = "localhost"  
MQTT_PORT = 1883
MQTT_TOPIC = "SIMULATOR/USER_AFFECTIVE_STATE"

class VAPickerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gerador de Vetor VA do Usário para o ROSE")
        self.root.geometry("450x550")
        self.root.resizable(False, False)
        
        # Conexão MQTT
        self.mqtt_client = mqtt.Client()
        try:
            self.mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
            self.mqtt_client.loop_start()
        except Exception as e:
            print(f"[Aviso] Não foi possível conectar ao broker MQTT: {e}")

        # Vetor VAD Inicial (valores de -1.0 a 1.0)
        self.v_val = 0.0
        self.a_val = 0.0
        self.d_val = 0.0 # Padrão neutro para o espaço 2D
        
        self.canvas_size = 350
        self.center = self.canvas_size / 2
        
        # Dicionário com as coordenadas das emoções para plotagem visual (V, A)
        self.emocoes_referencia = {
            "Alegria": (0.76, 0.48),
            "Surpresa": (0.40, 0.67),
            "Raiva": (-0.43, 0.67),
            "Nojo": (-0.60, 0.35),
            "Tristeza": (-0.63, -0.27),  # Invertido para -0.27 pois no plano cartesiano tradicional Excitação/Arousal baixa é negativo
            "Medo": (-0.64, 0.60),
            "Neutro": (0.00, 0.00)
        }
        
        self.setup_ui()

    def setup_ui(self):
        # Frame do Gráfico
        graph_frame = tk.LabelFrame(self.root, text=" Espaço Valence-Arousal (Clique para marcar) ", padx=10, pady=10)
        graph_frame.pack(pady=10)
        
        # Canvas para desenhar o plano cartesiano
        self.canvas = tk.Canvas(graph_frame, width=self.canvas_size, height=self.canvas_size, bg="white", highlightthickness=1, highlightbackground="#ccc")
        self.canvas.pack()
        
        # Desenha os eixos cartesianos principais (X e Y)
        self.canvas.create_line(0, self.center, self.canvas_size, self.center, fill="#aaa", dash=(4, 4)) # Eixo V
        self.canvas.create_line(self.center, 0, self.center, self.canvas_size, fill="#aaa", dash=(4, 4)) # Eixo A
        
        # Rótulos das Extremidades dos Eixos
        self.canvas.create_text(self.canvas_size - 25, self.center + 15, text="+V", fill="green", font=("Arial", 8, "bold"))
        self.canvas.create_text(25, self.center + 15, text="-V", fill="red", font=("Arial", 8, "bold"))
        self.canvas.create_text(self.center + 15, 15, text="+A", fill="orange", font=("Arial", 8, "bold"))
        self.canvas.create_text(self.center + 15, self.canvas_size - 15, text="-A", fill="blue", font=("Arial", 8, "bold"))
        
        # --- NOVO: Plotagem das Emoções de Referência ---
        for nome, (v, a) in self.emocoes_referencia.items():
            # Converte a coordenada matemática (-1 a 1) para pixels do Canvas
            x_p = (v * self.center) + self.center
            y_p = self.center - (a * self.center) # Eixo Y invertido no Tkinter
            
            if nome != "Neutro":  # Evita desenhar por cima do ponto inicial central
                # Desenha um pequeno ponto guia cinza
                self.canvas.create_oval(x_p-3, y_p-3, x_p+3, y_p+3, fill="#888", outline="#666")
            
            # Adiciona o rótulo de texto sutil perto da coordenada
            # Desloca o texto um pouco para cima (y_p - 10) para não ficar colado no ponto
            self.canvas.create_text(x_p, y_p - 10, text=nome, fill="#555", font=("Arial", 8, "italic"))
        
        # Cria a marcação visual do ponto selecionável atual (inicia no centro)
        self.point = self.canvas.create_oval(self.center-6, self.center-6, self.center+6, self.center+6, fill="red", outline="black")
        
        # Bind do clique do mouse no Canvas
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        
        # Frame de Informações e Envio
        control_frame = tk.Frame(self.root)
        control_frame.pack(fill="x", padx=20, pady=10)

        # Labels para exibir o vetor atual
        self.vector_label = tk.Label(control_frame, text="Vetor Atual VAD: [0.00, 0.00, 0.00]", font=("Arial", 11, "bold"))
        self.vector_label.pack(pady=5)
        
        # Botão Enviar por MQTT
        send_btn = tk.Button(control_frame, text="Enviar Vetor do Usuário por MQTT", bg="#4CAF50", fg="white", font=("Arial", 11, "bold"), height=2, command=self.send_mqtt_message)
        send_btn.pack(fill="x", pady=5)

    def on_canvas_click(self, event):
        x, y = event.x, event.y
        
        x = max(0, min(x, self.canvas_size))
        y = max(0, min(y, self.canvas_size))
        
        self.canvas.coords(self.point, x-6, y-6, x+6, y+6)
        
        self.v_val = (x - self.center) / self.center
        self.a_val = -(y - self.center) / self.center
        
        self.v_val = round(max(-1.0, min(self.v_val, 1.0)), 2)
        self.a_val = round(max(-1.0, min(self.a_val, 1.0)), 2)
        
        # Mapeamento estático opcional para injetar a dominância correspondente se clicar exatamente nas marcas
        # Por padrão para o clique livre, mantemos a dominância que você usa (ou 0.0)
        self.vector_label.config(text=f"Vetor Atual VAD: [{self.v_val:.2f}, {self.a_val:.2f}, {self.d_val:.2f}]")

    def send_mqtt_message(self):
        payload = f"{self.v_val} {self.a_val} {self.d_val}"
        
        try:
            result = self.mqtt_client.publish(MQTT_TOPIC, payload, qos=1)
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                print(f"[MQTT] Publicado com sucesso no tópico {MQTT_TOPIC}: {payload}")
                self.vector_label.config(fg="green")
                self.root.after(500, lambda: self.vector_label.config(fg="black"))
            else:
                raise Exception("Erro no código de retorno do Broker.")
        except Exception as e:
            messagebox.showerror("Erro MQTT", f"Falha ao enviar mensagem: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = VAPickerApp(root)
    root.mainloop()