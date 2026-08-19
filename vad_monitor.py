import json
import os
import queue
import sys
import tkinter as tk
from pathlib import Path

import paho.mqtt.client as mqtt


BASE_DIR = Path(__file__).resolve().parent
parent_dir = os.path.abspath(os.path.join(BASE_DIR, "../"))

sys.path.append(parent_dir)
sys.path.append(os.path.join(os.getcwd(), "robot_package"))

import config
import robot_package.robot_profile as robot_profile


# --- CONFIGURAÇÃO MQTT ---
MQTT_BROKER = "localhost"
MQTT_PORT = 1883

robot_base_topic = robot_profile.ROBOT_BASE_TOPIC

TOPIC_ROBOT_AFFECTIVE_STATE = config.ROBOT_AFFECTIVE_STATE_TOPIC
TOPIC_USER_AFFECTIVE_STATE = config.USER_AFFECTIVE_STATE_TOPIC
TOPIC_BASE_MOOD = "BASE_MOOD"


class VAMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Robot and User Affective State Monitor")
        self.root.geometry("450x500")
        self.root.resizable(False, False)

        # Fila para comunicação segura entre a thread do MQTT
        # e a thread principal do Tkinter
        self.msg_queue = queue.Queue()

        self.canvas_size = 350
        self.center = self.canvas_size / 2

        # Coordenadas dos níveis mais intensos das emoções
        self.emocoes_referencia = {
            "Happiness": (0.76, 0.48),
            "Anger": (-0.43, 0.67),
            "Sadness": (-0.63, -0.27),
            "Neutral": (0.00, 0.00)
        }

        # Cores dos níveis emocionais.
        # L1 é o nível mais claro e L4 é o mais intenso.
        self.emotion_level_colors = {
            "Happiness": [
                "#D9F99D",  # L1
                "#BEF264",  # L2
                "#84CC16",  # L3
                "#00FF00"   # L4
            ],
            "Anger": [
                "#FECACA",  # L1
                "#FCA5A5",  # L2
                "#F87171",  # L3
                "#FF0000"   # L4
            ],
            "Sadness": [
                "#DBEAFE",  # L1
                "#93C5FD",  # L2
                "#60A5FA",  # L3
                "#0000FF"   # L4
            ]
        }

        self.setup_ui()
        self.setup_mqtt()
        self.check_queue_loop()

        self.root.protocol(
            "WM_DELETE_WINDOW",
            self.close_application
        )

    def setup_ui(self):
        # --- FRAME DO GRÁFICO ---
        graph_frame = tk.LabelFrame(
            self.root,
            text=" Valence and Arousal Affective Space ",
            padx=10,
            font=("Arial", 10, "bold"),
            pady=10
        )
        graph_frame.pack(pady=10)

        self.canvas = tk.Canvas(
            graph_frame,
            width=self.canvas_size,
            height=self.canvas_size,
            bg="white",
            highlightthickness=1,
            highlightbackground="#ccc"
        )
        self.canvas.pack()

        # Eixo horizontal: Valence
        self.canvas.create_line(
            0,
            self.center,
            self.canvas_size,
            self.center,
            fill="#aaa",
            dash=(4, 4)
        )

        # Eixo vertical: Arousal
        self.canvas.create_line(
            self.center,
            0,
            self.center,
            self.canvas_size,
            fill="#aaa",
            dash=(4, 4)
        )

        # Rótulos dos eixos
        self.canvas.create_text(
            self.canvas_size - 25,
            self.center + 15,
            text="+V",
            fill="black",
            font=("Arial", 8, "bold")
        )

        self.canvas.create_text(
            25,
            self.center + 15,
            text="-V",
            fill="black",
            font=("Arial", 8, "bold")
        )

        self.canvas.create_text(
            self.center + 15,
            15,
            text="+A",
            fill="black",
            font=("Arial", 8, "bold")
        )

        self.canvas.create_text(
            self.center + 15,
            self.canvas_size - 15,
            text="-A",
            fill="black",
            font=("Arial", 8, "bold")
        )

        # --- EMOÇÕES E NÍVEIS DE INTENSIDADE ---
        self.draw_emotion_levels()

        # --- ÍCONE DO ROBÔ ---
        self.robot_parts = {}

        self.robot_parts["head"] = self.canvas.create_rectangle(
            self.center - 6,
            self.center - 6,
            self.center + 6,
            self.center + 6,
            fill="#CBD5E1",
            outline="#1E293B",
            width=1.5
        )

        self.robot_parts["eye_l"] = self.canvas.create_oval(
            self.center - 4,
            self.center - 3,
            self.center - 2,
            self.center - 1,
            fill="#007BFF",
            outline=""
        )

        self.robot_parts["eye_r"] = self.canvas.create_oval(
            self.center + 2,
            self.center - 3,
            self.center + 4,
            self.center - 1,
            fill="#007BFF",
            outline=""
        )

        self.robot_parts["mouth"] = self.canvas.create_line(
            self.center - 3,
            self.center + 2,
            self.center + 3,
            self.center + 2,
            fill="#1E293B",
            width=1.5
        )

        self.robot_parts["antenna"] = self.canvas.create_line(
            self.center,
            self.center - 6,
            self.center,
            self.center - 9,
            fill="#1E293B",
            width=1.5
        )

        self.robot_parts["antenna_tip"] = self.canvas.create_oval(
            self.center - 1,
            self.center - 11,
            self.center + 1,
            self.center - 9,
            fill="#EF4444",
            outline=""
        )

        # --- ÍCONE DO USUÁRIO ---
        self.user_parts = {}

        self.user_parts["head"] = self.canvas.create_oval(
            self.center - 5,
            self.center - 10,
            self.center + 5,
            self.center,
            fill="#FFCC99",
            outline="#664422",
            width=1.5
        )

        self.user_parts["body"] = self.canvas.create_arc(
            self.center - 10,
            self.center,
            self.center + 10,
            self.center + 16,
            start=0,
            extent=180,
            fill="#34D399",
            outline="#065F46",
            width=1.5
        )

        # --- FRAME DE INFORMAÇÕES ---
        control_frame = tk.Frame(self.root)
        control_frame.pack(
            fill="x",
            padx=20,
            pady=5
        )

        self.robot_label = tk.Label(
            control_frame,
            text="Robot VAD: Waiting...",
            font=("Arial", 10, "bold"),
            fg="#475569"
        )
        self.robot_label.pack(pady=2)

        self.user_label = tk.Label(
            control_frame,
            text="User VAD: Waiting...",
            font=("Arial", 10, "bold"),
            fg="#475569"
        )
        self.user_label.pack(pady=2)

        self.base_mood_label = tk.Label(
            control_frame,
            text="Base Mood VAD: Waiting...",
            font=("Arial", 10, "bold"),
            fg="#475569"
        )
        self.base_mood_label.pack(pady=2)

    def draw_emotion_levels(self):
        """
        Desenha o neutro no centro e quatro níveis para cada emoção.

        Os níveis são posicionados em:
        L1 = 25% da coordenada emocional
        L2 = 50% da coordenada emocional
        L3 = 75% da coordenada emocional
        L4 = 100% da coordenada emocional
        """
        point_size = 4

        # Desenha primeiro as linhas que ligam o neutro às emoções.
        for name, (valence, arousal) in self.emocoes_referencia.items():
            if name == "Neutral":
                continue

            final_x = (
                valence * self.center
            ) + self.center

            final_y = self.center - (
                arousal * self.center
            )

            self.canvas.create_line(
                self.center,
                self.center,
                final_x,
                final_y,
                fill="#D1D5DB",
                dash=(2, 3)
            )

        # Desenha os níveis de cada emoção.
        for name, (valence, arousal) in self.emocoes_referencia.items():

            # O neutro permanece apenas no centro.
            if name == "Neutral":
                self.canvas.create_oval(
                    self.center - point_size,
                    self.center - point_size,
                    self.center + point_size,
                    self.center + point_size,
                    fill="#CCCCCC",
                    outline="#FFFFFF"
                )

                self.canvas.create_text(
                    self.center,
                    self.center - 13,
                    text="Neutral",
                    fill="#000000",
                    font=("Arial", 9)
                )

                continue

            colors = self.emotion_level_colors[name]

            # Cria L1, L2, L3 e L4.
            for level in range(1, 5):
                proportion = level / 4

                level_valence = valence * proportion
                level_arousal = arousal * proportion

                x_position = (
                    level_valence * self.center
                ) + self.center

                y_position = self.center - (
                    level_arousal * self.center
                )

                self.canvas.create_oval(
                    x_position - point_size,
                    y_position - point_size,
                    x_position + point_size,
                    y_position + point_size,
                    fill=colors[level - 1],
                    outline="#ffffff"
                )

                # Os pontos intermediários recebem L1, L2 e L3.
                # O ponto original recebe o nome da emoção.
                if level < 4:
                    label = f"L{level}"
                    font = ("Arial", 7)
                else:
                    label = name
                    font = ("Arial", 9)

                if name == "Sadness" and level == 4:
                    text_y = y_position + 13
                else:
                    text_y = y_position - 13

                self.canvas.create_text(
                    x_position,
                    text_y,
                    text=label,
                    fill="#000000",
                    font=font
                )

    def setup_mqtt(self):
        self.mqtt_client = mqtt.Client()

        self.mqtt_client.on_connect = self.on_mqtt_connect
        self.mqtt_client.on_message = self.on_mqtt_message

        try:
            self.mqtt_client.connect(
                MQTT_BROKER,
                MQTT_PORT,
                60
            )

            self.mqtt_client.loop_start()

        except Exception as error:
            print(
                f"Erro ao conectar ao broker MQTT: {error}"
            )

    def on_mqtt_connect(self, client, userdata, flags, rc):
        if rc == 0:
            robot_topic = (
                robot_base_topic
                + "/"
                + TOPIC_ROBOT_AFFECTIVE_STATE
            )

            user_topic = (
                robot_base_topic
                + "/"
                + TOPIC_USER_AFFECTIVE_STATE
            )

            base_mood_topic = (
                robot_base_topic
                + "/"
                + TOPIC_BASE_MOOD
            )

            self.mqtt_client.subscribe(robot_topic)
            self.mqtt_client.subscribe(user_topic)
            self.mqtt_client.subscribe(base_mood_topic)

            print(f"[MQTT] Inscrito em: {robot_topic}")
            print(f"[MQTT] Inscrito em: {user_topic}")
            print(f"[MQTT] Inscrito em: {base_mood_topic}")

        else:
            print(
                f"Falha na conexão MQTT. Código: {rc}"
            )

    def on_mqtt_message(self, client, userdata, msg):
        try:
            payload = msg.payload.decode("utf-8")

            self.msg_queue.put(
                (msg.topic, payload)
            )

        except UnicodeDecodeError as error:
            print(
                f"Erro ao decodificar mensagem MQTT: {error}"
            )

    def check_queue_loop(self):
        try:
            while True:
                topic, payload = self.msg_queue.get_nowait()

                self.update_telemetry(
                    topic,
                    payload
                )

                self.msg_queue.task_done()

        except queue.Empty:
            pass

        finally:
            self.root.after(
                50,
                self.check_queue_loop
            )

    def update_telemetry(self, topic, payload_str):
        try:
            vad_data = json.loads(payload_str)

            v_val = float(
                vad_data.get("valence", 0.0)
            )

            a_val = float(
                vad_data.get("arousal", 0.0)
            )

            d_val = float(
                vad_data.get("dominance", 0.0)
            )

            robot_topic = (
                robot_base_topic
                + "/"
                + TOPIC_ROBOT_AFFECTIVE_STATE
            )

            user_topic = (
                robot_base_topic
                + "/"
                + TOPIC_USER_AFFECTIVE_STATE
            )

            base_mood_topic = (
                robot_base_topic
                + "/"
                + TOPIC_BASE_MOOD
            )

            # O Base Mood somente atualiza seu texto.
            if topic == base_mood_topic:
                self.base_mood_label.config(
                    text=(
                        f"Base Mood VAD: "
                        f"[{v_val:.2f}, "
                        f"{a_val:.2f}, "
                        f"{d_val:.2f}]"
                    )
                )

                print(
                    f"[BASE MOOD] "
                    f"[{v_val:.2f}, "
                    f"{a_val:.2f}, "
                    f"{d_val:.2f}]"
                )

                return

            # Conversão da escala VA para pixels.
            x_pixel = (
                v_val * self.center
            ) + self.center

            y_pixel = self.center - (
                a_val * self.center
            )

            # Impede que os ícones saiam do canvas.
            x_pixel = max(
                15,
                min(x_pixel, self.canvas_size - 15)
            )

            y_pixel = max(
                15,
                min(y_pixel, self.canvas_size - 15)
            )

            if topic == robot_topic:
                self.robot_label.config(
                    text=(
                        f"Robot VAD: "
                        f"[{v_val:.2f}, "
                        f"{a_val:.2f}, "
                        f"{d_val:.2f}]"
                    )
                )

                parts_dict = self.robot_parts

                current_coords = self.canvas.coords(
                    parts_dict["head"]
                )

                current_x = (
                    current_coords[0]
                    + current_coords[2]
                ) / 2

                current_y = (
                    current_coords[1]
                    + current_coords[3]
                ) / 2

            elif topic == user_topic:
                self.user_label.config(
                    text=(
                        f"User VAD: "
                        f"[{v_val:.2f}, "
                        f"{a_val:.2f}, "
                        f"{d_val:.2f}]"
                    )
                )

                parts_dict = self.user_parts

                current_coords = self.canvas.coords(
                    parts_dict["head"]
                )

                current_x = (
                    current_coords[0]
                    + current_coords[2]
                ) / 2

                current_y = (
                    (
                        current_coords[1]
                        + current_coords[3]
                    ) / 2
                ) + 5

            else:
                return

            dx = x_pixel - current_x
            dy = y_pixel - current_y

            for part_id in parts_dict.values():
                self.canvas.move(
                    part_id,
                    dx,
                    dy
                )

            self.root.update_idletasks()

        except json.JSONDecodeError as error:
            print(
                f"[Erro JSON] Tópico {topic} enviou "
                f"uma mensagem inválida: {payload_str}. "
                f"Detalhes: {error}"
            )

        except (TypeError, ValueError) as error:
            print(
                f"[Erro VAD] Valores inválidos recebidos "
                f"no tópico {topic}: {payload_str}. "
                f"Detalhes: {error}"
            )

        except Exception as error:
            print(
                f"[Erro de Parse] Tópico {topic} enviou "
                f"a mensagem: '{payload_str}'. "
                f"Detalhes: {error}"
            )

    def close_application(self):
        try:
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()

        except Exception as error:
            print(
                f"Erro ao encerrar a conexão MQTT: {error}"
            )

        finally:
            self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = VAMonitorApp(root)
    root.mainloop()