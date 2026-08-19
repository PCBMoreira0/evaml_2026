import json
import os
import sys
import tkinter as tk
from pathlib import Path
from tkinter import messagebox

import paho.mqtt.client as mqtt


BASE_DIR = Path(__file__).resolve().parent
parent_dir = os.path.abspath(os.path.join(BASE_DIR, "../"))

sys.path.append(parent_dir)
sys.path.append(os.path.join(os.getcwd(), "robot_package"))

import config
import robot_package.robot_profile as robot_profile


# --- CONFIGURAÇÃO MQTT ---
MQTT_BROKER = config.MQTT_BROKER_ADRESS
MQTT_PORT = config.MQTT_PORT

robot_base_topic = robot_profile.ROBOT_BASE_TOPIC
MQTT_TOPIC = robot_base_topic + "/ROBOT_AFFECTIVE_PROFILE"


class VAParametersApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Robot Affective Profile Parameters - Manual Configuration")
        self.root.geometry("680x570")
        self.root.resizable(False, False)

        # Conexão MQTT
        self.mqtt_client = mqtt.Client()

        try:
            self.mqtt_client.connect(
                MQTT_BROKER,
                MQTT_PORT,
                60
            )
            self.mqtt_client.loop_start()

        except Exception as error:
            print(
                f"Não foi possível conectar ao broker MQTT: {error}"
            )

        self.setup_ui()

        # Encerra corretamente a conexão MQTT ao fechar a janela
        self.root.protocol(
            "WM_DELETE_WINDOW",
            self.close_application
        )

    def setup_ui(self):
        # # --- CABEÇALHO PRINCIPAL ---
        # header_label = tk.Label(
        #     self.root,
        #     text="Robot Affective Profile Parameters",
        #     font=("Arial", 16, "bold"),
        #     fg="#1e293b"
        # )
        # header_label.pack(pady=20)

        # --- CONTAINER 1: EMPATHY FACTOR ---
        empathy_frame = tk.LabelFrame(
            self.root,
            text=(
                "Empathy Factor (e) - Controls the influence of "
                "the user's affective state."
            ),
            padx=15,
            pady=10,
            font=("Arial", 11, "bold")
        )
        empathy_frame.pack(
            fill="x",
            padx=30,
            pady=20
        )

        self.scale_empathy = tk.Scale(
            empathy_frame,
            from_=0.0,
            to=1.0,
            resolution=0.1,
            orient="horizontal",
            font=("Arial", 11),
            length=450
        )
        self.scale_empathy.set(0.40)
        self.scale_empathy.pack(pady=0)

        # --- CONTAINER 2: EMOTIONAL DECAY FACTOR ---
        decay_frame = tk.LabelFrame(
            self.root,
            text=(
                "Emotional Decay Factor (d) - Controls the rate "
                "of convergence toward the base mood."
            ),
            padx=15,
            pady=10,
            font=("Arial", 11, "bold")
        )
        decay_frame.pack(
            fill="x",
            padx=30,
            pady=10
        )

        self.scale_decay = tk.Scale(
            decay_frame,
            from_=0.0,
            to=1.0,
            resolution=0.1,
            orient="horizontal",
            font=("Arial", 11),
            length=450
        )
        self.scale_decay.set(0.5)
        self.scale_decay.pack(pady=5)

        # --- CONTAINER 3: DECAY DELAY ---
        decay_delay_frame = tk.LabelFrame(
            self.root,
            text=(
                "Decay Delay (ℓ) [s] - Defines the delay before "
                "emotional decay begins."
            ),
            padx=15,
            pady=10,
            font=("Arial", 11, "bold")
        )
        decay_delay_frame.pack(
            fill="x",
            padx=30,
            pady=10
        )

        self.scale_decay_delay = tk.Scale(
            decay_delay_frame,
            from_=0.0,
            to=10.0,
            resolution=0.1,
            orient="horizontal",
            font=("Arial", 11),
            length=450
        )
        self.scale_decay_delay.set(2.0)
        self.scale_decay_delay.pack(pady=5)

        # --- CONTAINER 4: BASE MOOD ---
        mood_frame = tk.LabelFrame(
            self.root,
            text="Base Mood (Valence and Arousal Components)",
            padx=15,
            pady=10,
            font=("Arial", 11, "bold")
        )
        mood_frame.pack(
            fill="x",
            padx=30,
            pady=10
        )

        # Faz a segunda coluna ocupar o espaço disponível
        mood_frame.grid_columnconfigure(
            1,
            weight=1
        )

        # --- VALENCE ---
        valence_label = tk.Label(
            mood_frame,
            text="Valence:",
            font=("Arial", 10, "bold"),
            width=9,
            anchor="w"
        )
        valence_label.grid(
            row=0,
            column=0,
            padx=(0, 10),
            pady=2,
            sticky="w"
        )

        self.scale_mood_v = tk.Scale(
            mood_frame,
            from_=-1.0,
            to=1.0,
            resolution=0.05,
            orient="horizontal",
            font=("Arial", 10),
            length=430
        )
        self.scale_mood_v.set(0.0)
        self.scale_mood_v.grid(
            row=0,
            column=1,
            pady=2,
            sticky="ew"
        )

        # --- AROUSAL ---
        arousal_label = tk.Label(
            mood_frame,
            text="Arousal:",
            font=("Arial", 10, "bold"),
            width=9,
            anchor="w"
        )
        arousal_label.grid(
            row=1,
            column=0,
            padx=(0, 10),
            pady=2,
            sticky="w"
        )

        self.scale_mood_a = tk.Scale(
            mood_frame,
            from_=-1.0,
            to=1.0,
            resolution=0.05,
            orient="horizontal",
            font=("Arial", 10),
            length=430
        )
        self.scale_mood_a.set(0.0)
        self.scale_mood_a.grid(
            row=1,
            column=1,
            pady=2,
            sticky="ew"
        )

        # --- BOTÃO DE ENVIO ---
        send_button = tk.Button(
            self.root,
            text="Send Affective Profile Parameters via MQTT",
            bg="#2563EB",
            fg="white",
            font=("Arial", 14, "bold"),
            height=1,
            command=self.send_parameters
        )
        send_button.pack(
            fill="x",
            padx=30,
            pady=5
        )

    def send_parameters(self):
        # Coleta os valores atuais dos sliders
        empathy = self.scale_empathy.get()
        decay = self.scale_decay.get()
        delay = self.scale_decay_delay.get()

        mood_v = self.scale_mood_v.get()
        mood_a = self.scale_mood_a.get()
        mood_d = 0.0

        payload_data = {
            "profile": "xxx",
            "empathy": empathy,
            "decay": decay,
            "delay": delay,
            "mood": {
                "valence": mood_v,
                "arousal": mood_a,
                "dominance": mood_d
            }
        }

        payload = json.dumps(payload_data)

        print(payload)

        try:
            result = self.mqtt_client.publish(
                MQTT_TOPIC,
                payload,
                qos=1
            )

            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                print(
                    f"[MQTT] Parâmetros publicados em "
                    f"{MQTT_TOPIC}: {payload}"
                )
            else:
                raise RuntimeError(
                    f"Código de retorno MQTT inválido: {result.rc}"
                )

        except Exception as error:
            messagebox.showerror(
                "Erro MQTT",
                f"Falha ao enviar parâmetros: {error}"
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
    app = VAParametersApp(root)
    root.mainloop()