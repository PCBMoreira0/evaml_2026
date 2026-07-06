import tkinter as tk
import paho.mqtt.client as mqtt
import queue

# --- CONFIGURAÇÃO MQTT ---
MQTT_BROKER = "localhost"  # Altere para o IP da máquina onde roda o ROSE/SENSEI
MQTT_PORT = 1883
MQTT_TOPIC = "SIMULATOR/ROBOT_EMOTION"

class VAMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Monitor de Estado Afetivo do Robô (ROSE)")
        self.root.geometry("450x550")
        self.root.resizable(False, False)
        
        # Fila para comunicação segura entre a Thread do MQTT e a do Tkinter
        self.msg_queue = queue.Queue()
        
        # Configuração das variáveis de estado (Valores iniciais no centro)
        self.v_val = 0.0
        self.a_val = 0.0
        self.d_val = 0.0
        
        self.canvas_size = 350
        self.center = self.canvas_size / 2
        
        # Dicionário com as coordenadas das emoções para plotagem visual (V, A)
        self.emocoes_referencia = {
            "Alegria (A4)": (0.76, 0.48),
            "A1": (0.24, 0.12),
            "A2": (0.41, 0.26),
            "A3": (0.6, 0.38),
            "Surpresa (S4)": (0.40, 0.67),
            "S1": (0.12, 0.18),
            "S2": (0.21, 0.35),
            "S3": (0.31, 0.50),
            "Raiva (R4)": (-0.43, 0.67),
            "R1": (-0.11, 0.16),
            "R2": (-0.22, 0.32),
            "R3": (-0.32, 0.48),
            "Trist. (T4)": (-0.63, -0.27),  # Ajustado para o quadrante inferior (-A)
            "T1": (-0.18, -0.08),
            "T2": (-0.32, -0.15),
            "T3": (-0.44, -0.20),
            "Neutro": (0.00, 0.00)
        }
        
        # Inicializa a UI e a conexão MQTT
        self.setup_ui()
        self.setup_mqtt()
        
        # Inicia o loop de verificação da fila de mensagens para atualizar a tela
        self.check_queue_loop()

    def setup_ui(self):
        # Frame do Gráfico
        graph_frame = tk.LabelFrame(self.root, text=" Transformação Empática do Robô - Valence-Arousal (Tempo Real) ", padx=10, pady=10)
        graph_frame.pack(pady=10)
        
        # Canvas para desenhar o plano cartesiano
        self.canvas = tk.Canvas(graph_frame, width=self.canvas_size, height=self.canvas_size, bg="white", highlightthickness=1, highlightbackground="#ccc")
        self.canvas.pack()
        
        # Desenha os eixos cartesianos (X e Y)
        self.canvas.create_line(0, self.center, self.canvas_size, self.center, fill="#aaa", dash=(4, 4)) # Eixo V
        self.canvas.create_line(self.center, 0, self.center, self.canvas_size, fill="#aaa", dash=(4, 4)) # Eixo A
        
        # Rótulos das Extremidades dos Eixos
        self.canvas.create_text(self.canvas_size - 25, self.center + 15, text="+V", fill="green", font=("Arial", 8, "bold"))
        self.canvas.create_text(25, self.center + 15, text="-V", fill="red", font=("Arial", 8, "bold"))
        self.canvas.create_text(self.center + 15, 15, text="+A", fill="orange", font=("Arial", 8, "bold"))
        self.canvas.create_text(self.center + 15, self.canvas_size - 15, text="-A", fill="blue", font=("Arial", 8, "bold"))
        
        # --- Plotagem das Emoções de Referência (Guias de Fundo) ---
        for nome, (v, a) in self.emocoes_referencia.items():
            x_p = (v * self.center) + self.center
            y_p = self.center - (a * self.center)
            
            if nome != "Neutro":  # Evita desenhar por cima do ponto inicial central
                if nome == "Raiva (R4)":
                    self.canvas.create_oval(x_p-4, y_p-4, x_p+4, y_p+4, fill="#ff0000", outline="#aaa")
                elif nome=="R1" or nome=="R2" or nome=="R3":
                    self.canvas.create_oval(x_p-2, y_p-2, x_p+2, y_p+2, fill="#ff0000", outline="#aaa")

                elif nome == "Trist. (T4)":
                    self.canvas.create_oval(x_p-4, y_p-4, x_p+4, y_p+4, fill="#0000ff", outline="#aaa")
                elif nome=="T1" or nome=="T2" or nome=="T3":
                    self.canvas.create_oval(x_p-2, y_p-2, x_p+2, y_p+2, fill="#0000ff", outline="#aaa")

                elif nome == "Surpresa (S4)":
                    self.canvas.create_oval(x_p-4, y_p-4, x_p+4, y_p+4, fill="#ffff00", outline="#aaa")
                elif nome=="S1" or nome=="S2" or nome=="S3":
                    self.canvas.create_oval(x_p-2, y_p-2, x_p+2, y_p+2, fill="#ffff00", outline="#aaa")

                elif nome == "Alegria (A4)":
                    self.canvas.create_oval(x_p-4, y_p-4, x_p+4, y_p+4, fill="#00ff00", outline="#aaa")
                elif nome=="A1" or nome=="A2" or nome=="A3":
                    self.canvas.create_oval(x_p-2, y_p-2, x_p+2, y_p+2, fill="#00ff00", outline="#aaa")
                    
                else:
                    self.canvas.create_oval(x_p-3, y_p-3, x_p+3, y_p+3, fill="#ccc", outline="#aaa")
            
            
            self.canvas.create_text(x_p, y_p - 12, text=nome, fill="#777", font=("Arial", 8, "italic"))
        
        # --- CONSTRUÇÃO DO ROBÔ VETORIAL (Dimensões Reduzidas à Metade) ---
        self.robot_parts = {}
        
        # Carcaça da cabeça (Quadrado reduzido de 24x24 para 12x12 pixels)
        self.robot_parts["head"] = self.canvas.create_rectangle(
            self.center-6, self.center-6, self.center+6, self.center+6, 
            fill="#CBD5E1", outline="#1E293B", width=1.5
        )
        # Olho Esquerdo
        self.robot_parts["eye_l"] = self.canvas.create_oval(
            self.center-4, self.center-3, self.center-2, self.center-1, 
            fill="#007BFF", outline=""
        )
        # Olho Direito
        self.robot_parts["eye_r"] = self.canvas.create_oval(
            self.center+2, self.center-3, self.center+4, self.center-1, 
            fill="#007BFF", outline=""
        )
        # Boca (Linha horizontal encurtada)
        self.robot_parts["mouth"] = self.canvas.create_line(
            self.center-3, self.center+2, self.center+3, self.center+2, 
            fill="#1E293B", width=1.5
        )
        # Haste da Antena
        self.robot_parts["antenna"] = self.canvas.create_line(
            self.center, self.center-6, self.center, self.center-9, 
            fill="#1E293B", width=1.5
        )
        # Ponta da Antena
        self.robot_parts["antenna_tip"] = self.canvas.create_oval(
            self.center-1, self.center-11, self.center+1, self.center-9, 
            fill="#EF4444", outline=""
        )
        
        # Frame de Informações e Status
        control_frame = tk.Frame(self.root)
        control_frame.pack(fill="x", padx=20, pady=10)
        
        # Labels para exibir o vetor recebido por MQTT
        self.vector_label = tk.Label(control_frame, text="Aguardando dados do framework...", font=("Arial", 11, "bold"), fg="#555")
        self.vector_label.pack(pady=5)
        
        # Indicador de Status da Conexão
        self.status_label = tk.Label(control_frame, text="Status MQTT: Desconectado", font=("Arial", 9, "italic"), fg="red")
        self.status_label.pack(pady=5)

    def setup_mqtt(self):
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self.on_mqtt_connect
        self.mqtt_client.on_message = self.on_mqtt_message
        
        try:
            self.mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
            self.mqtt_client.loop_start()
        except Exception as e:
            self.status_label.config(text=f"Erro de Conexão: {e}", fg="red")

    def on_mqtt_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.status_label.config(text=f"Conectado ao Broker (Tópico: {MQTT_TOPIC})", fg="green")
            self.mqtt_client.subscribe(MQTT_TOPIC)
        else:
            self.status_label.config(text=f"Falha na conexão. Código: {rc}", fg="red")

    def on_mqtt_message(self, client, userdata, msg):
        payload_str = msg.payload.decode('utf-8')
        self.msg_queue.put(payload_str)
        print(payload_str)

    def check_queue_loop(self):
        try:
            while True:
                payload_str = self.msg_queue.get_nowait()
                self.update_telemetry(payload_str)
                self.msg_queue.task_done()
        except queue.Empty:
            pass
        finally:
            self.root.after(50, self.check_queue_loop)

    def update_telemetry(self, payload_str):
        try:
            # 1. Limpa espaços nas pontas e remove os colchetes
            payload_cleaned = payload_str.strip().strip("[]")
            
            # 2. Divide limpando múltiplos espaços do NumPy
            parts = payload_cleaned.split()
            
            if len(parts) >= 2:
                self.v_val = float(parts[0])
                self.a_val = float(parts[1])
                self.d_val = float(parts[2]) if len(parts) == 3 else 0.0
                
                # Atualiza o texto informativo da interface
                self.vector_label.config(
                    text=f"Vetor Robô VAD: [{self.v_val:.2f}, {self.a_val:.2f}, {self.d_val:.2f}]", 
                    fg="black"
                )
                
                # --- Converte Escala VAD (-1.0 a 1.0) de volta para Pixels ---
                x_pixel = (self.v_val * self.center) + self.center
                y_pixel = self.center - (self.a_val * self.center)
                
                # Ajuste das margens limite para refletir o tamanho menor do robô
                x_pixel = max(8, min(x_pixel, self.canvas_size - 8))
                y_pixel = max(13, min(y_pixel, self.canvas_size - 8))
                
                # --- MOVIMENTAÇÃO DO GRUPO VETORIAL ---
                # Pega a posição central atual da cabeça
                current_coords = self.canvas.coords(self.robot_parts["head"])
                current_x = (current_coords[0] + current_coords[2]) / 2
                current_y = (current_coords[1] + current_coords[3]) / 2
                
                # Calcula o deslocamento relativo (Delta)
                dx = x_pixel - current_x
                dy = y_pixel - current_y
                
                # Move todas as partes do robozinho juntas
                for part_id in self.robot_parts.values():
                    self.canvas.move(part_id, dx, dy)
                
                # Força o redesenho imediato na tela
                self.root.update_idletasks()
                
        except Exception as e:
            print(f"[Erro de Parse] String recebida inválida: '{payload_str}'. Detalhes: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = VAMonitorApp(root)
    root.mainloop()