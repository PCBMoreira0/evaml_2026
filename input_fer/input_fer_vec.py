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

import robot_package.robot_profile as robot_profile

# 1. Configurações de ambiente para limpar o terminal de vez
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ["QT_LOGGING_RULES"] = "*.debug=false;*.warning=false;qt.qpa.fonts=false"

import cv2
import numpy as np
from deepface import DeepFace
import matplotlib.pyplot as plt


# 2. Configuração EKMAN_VAD_3D
EKMAN_VAD_3D = {
    "happy":    (0.76, 0.48, 0.35, "green"),       
    "angry":    (-0.51, 0.59, 0.25, "crimson"),    
    "sad":      (-0.63, -0.27, -0.33, "royalblue"), 
    "surprise": (0.40, 0.67, -0.13, "gold"),       
    "fear":     (-0.64, 0.60, -0.43, "purple"),     
    "disgust":  (-0.60, 0.35, 0.11, "saddlebrown"), 
    "neutral":  (0.00, 0.00, 0.00, "gray")          
}

# --- Classe para Histerese e Estabilização ---
class EmotionStabilizer:
    def __init__(self, alpha=0.8):
        self.alpha = alpha  
        self.v_smooth = 0.0
        self.a_smooth = 0.0
        self.d_smooth = 0.0

    def update(self, v_raw, a_raw, d_raw):
        self.v_smooth = (self.v_smooth * self.alpha) + (v_raw * (1 - self.alpha))
        self.a_smooth = (self.a_smooth * self.alpha) + (a_raw * (1 - self.alpha))
        self.d_smooth = (self.d_smooth * self.alpha) + (d_raw * (1 - self.alpha))
        return self.v_smooth, self.a_smooth, self.d_smooth

stabilizer = EmotionStabilizer(alpha=0.85)

# Inicializa captura (Webcam 1)
cap = cv2.VideoCapture(1) 

# Configuração fixa do gráfico Matplotlib 2D (Criado uma vez fora do loop)
plt.ion()
fig, ax = plt.subplots(figsize=(6, 6))
vetor_atual = None

def configurar_background_grafico():
    ax.set_xlim(-1, 1)
    ax.set_ylim(-1, 1)
    ax.axhline(0, color='black', lw=1, alpha=0.5)
    ax.axvline(0, color='black', lw=1, alpha=0.5)
    ax.set_xlabel('Valência (X)')
    ax.set_ylabel('Arousal (Y)')
    ax.set_title("Espaço VAD - Análise Estabilizada")
    for nome, (v, a, d, cor) in EKMAN_VAD_3D.items():
        ax.scatter(v, a, c=cor, s=120, alpha=0.4, edgecolors='black')
        ax.text(v + 0.03, a + 0.01, nome.upper(), fontsize=9, fontweight='bold', alpha=0.7)

# Executa a configuração fixa do gráfico inicial
configurar_background_grafico()

print("Iniciando... Ajustado para usar detector 'mediapipe'. Pressione Q para sair.")

contador = 0
ultimo_resultado = None
while True:
    ret, frame = cap.read()
    contador += 1
    if not ret: 
        break

    try:
        # Trocado para 'mediapipe' para evitar o erro fatal de arquivo xml do opencv
        if contador % 10 == 0:
            ultimo_resultado = DeepFace.analyze(
                frame,
                actions=['emotion'],
                enforce_detection=False,
                detector_backend='yunet',
                silent=True
            )

        # Se ainda não existe resultado, pula este frame
        if ultimo_resultado is None:
            continue

        results = ultimo_resultado
        
        for res in results:
            x, y, w, h = res['region']['x'], res['region']['y'], res['region']['w'], res['region']['h']
            emotions = res['emotion']
            
            v_raw, a_raw, d_raw = 0.0, 0.0, 0.0
            for emo_slug, prob in emotions.items():
                if emo_slug in EKMAN_VAD_3D:
                    v, a, d, _ = EKMAN_VAD_3D[emo_slug]
                    v_raw += (prob / 100) * v
                    a_raw += (prob / 100) * a
                    d_raw += (prob / 100) * d

            # Aplicação da Histerese
            v_f, a_f, d_f = stabilizer.update(v_raw, a_raw, d_raw)

            # Atualiza o Vetor no Gráfico sem apagar o texto estático de fundo
            if vetor_atual:
                vetor_atual.remove()
            vetor_atual = ax.quiver(0, 0, v_f, a_f, angles='xy', scale_units='xy', scale=1, color='black', width=0.012, zorder=5)
            
            # Desenho do Box Verde e rótulo na Webcam
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            label = f"V:{v_f:.2f} A:{a_f:.2f} D:{d_f:.2f}"
            cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # Lista de probabilidades lateral na webcam
            for i, (emo, prob) in enumerate(emotions.items()):
                text = f"{emo.upper()}: {prob:.1f}%"
                cv2.putText(frame, text, (x + w + 10, y + i * 20 + 20), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

        # Força o Matplotlib a redesenhar a janela de forma fluida
        fig.canvas.draw_idle()
        plt.pause(0.001)

    except Exception as e:
        # Se ocorrer qualquer erro, agora ele será impresso para você saber
        print(f"Erro interno: {e}")

    cv2.imshow('Analise Estabilizada - Q para sair', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
plt.close('all')