import os

# Configurações de ambiente antes de importar o DeepFace
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
os.environ["QT_LOGGING_RULES"] = (
    "*.debug=false;*.warning=false;qt.qpa.fonts=false"
)

import time

import cv2
import numpy as np
from deepface import DeepFace


# ============================================================
# CONFIGURAÇÕES
# ============================================================

CAMERA_INDEX = 1

CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480

# Executa o DeepFace a cada N frames
ANALYSIS_INTERVAL = 10

# Quanto maior, mais estável e mais lenta é a resposta
SMOOTHING_ALPHA = 0.85

# Largura do painel lateral de emoções
PANEL_WIDTH = 370

WINDOW_NAME = "Monitor de emoções - Q para sair"

EMOTION_NAMES = [
    "angry",
    "disgust",
    "fear",
    "happy",
    "sad",
    "surprise",
    "neutral",
]

# Cores no formato BGR, utilizado pelo OpenCV
EMOTION_COLORS = {
    "angry": (60, 20, 220),
    "disgust": (42, 42, 165),
    "fear": (150, 40, 130),
    "happy": (40, 180, 40),
    "sad": (220, 100, 40),
    "surprise": (20, 210, 240),
    "neutral": (150, 150, 150),
}


# ============================================================
# ESTABILIZADOR DE EMOÇÕES
# ============================================================

class EmotionStabilizer:
    def __init__(self, emotion_names, alpha=0.85):
        if not 0.0 <= alpha < 1.0:
            raise ValueError(
                "O valor de alpha deve estar no intervalo [0, 1)."
            )

        self.alpha = alpha

        self.values = {
            emotion: 0.0
            for emotion in emotion_names
        }

        self.initialized = False

    def update(self, emotions):
        """
        Aplica suavização exponencial:

        valor_suavizado =
            alpha * valor_anterior
            + (1 - alpha) * valor_atual
        """

        if not self.initialized:
            for emotion in self.values:
                self.values[emotion] = float(
                    emotions.get(emotion, 0.0)
                )

            self.initialized = True

        else:
            for emotion in self.values:
                current_value = float(
                    emotions.get(emotion, 0.0)
                )

                previous_value = self.values[emotion]

                self.values[emotion] = (
                    self.alpha * previous_value
                    + (1.0 - self.alpha) * current_value
                )

        return self.values.copy()


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def get_first_result(results):
    """
    Trata as possíveis estruturas retornadas pelo DeepFace.
    """

    if isinstance(results, list):
        if not results:
            return None

        return results[0]

    if isinstance(results, dict):
        return results

    return None


def get_dominant_emotion(emotions):
    if not emotions:
        return "neutral", 0.0

    dominant_emotion = max(
        emotions,
        key=emotions.get,
    )

    dominant_probability = float(
        emotions[dominant_emotion]
    )

    return dominant_emotion, dominant_probability


def draw_face_information(
    frame,
    region,
    emotions,
):
    """
    Desenha o retângulo da face e a emoção dominante.
    """

    frame_height, frame_width = frame.shape[:2]

    x = max(0, int(region.get("x", 0)))
    y = max(0, int(region.get("y", 0)))
    w = max(0, int(region.get("w", 0)))
    h = max(0, int(region.get("h", 0)))

    x2 = min(frame_width - 1, x + w)
    y2 = min(frame_height - 1, y + h)

    dominant_emotion, probability = (
        get_dominant_emotion(emotions)
    )

    color = EMOTION_COLORS.get(
        dominant_emotion,
        (0, 255, 0),
    )

    cv2.rectangle(
        frame,
        (x, y),
        (x2, y2),
        color,
        2,
    )

    label = (
        f"{dominant_emotion.upper()}: "
        f"{probability:.1f}%"
    )

    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.58
    thickness = 2

    text_size, baseline = cv2.getTextSize(
        label,
        font,
        font_scale,
        thickness,
    )

    text_width, text_height = text_size

    label_x = x

    if y - text_height - 14 >= 0:
        label_y = y - 8
        background_top = y - text_height - 14
        background_bottom = y
    else:
        label_y = y + text_height + 10
        background_top = y
        background_bottom = y + text_height + 16

    background_right = min(
        frame_width - 1,
        label_x + text_width + 12,
    )

    cv2.rectangle(
        frame,
        (label_x, background_top),
        (background_right, background_bottom),
        color,
        -1,
    )

    cv2.putText(
        frame,
        label,
        (label_x + 5, label_y),
        font,
        font_scale,
        (255, 255, 255),
        thickness,
        cv2.LINE_AA,
    )


def draw_emotion_panel(
    frame_height,
    emotions,
    fps,
):
    """
    Cria o painel lateral com as barras das emoções.
    """

    panel = np.full(
        (
            frame_height,
            PANEL_WIDTH,
            3,
        ),
        28,
        dtype=np.uint8,
    )

    # Título
    cv2.putText(
        panel,
        "EMOCOES DETECTADAS",
        (22, 38),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.67,
        (235, 235, 235),
        2,
        cv2.LINE_AA,
    )

    dominant_emotion, dominant_probability = (
        get_dominant_emotion(emotions)
    )

    dominant_color = EMOTION_COLORS.get(
        dominant_emotion,
        (180, 180, 180),
    )

    # Emoção dominante
    cv2.putText(
        panel,
        dominant_emotion.upper(),
        (22, 74),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.78,
        dominant_color,
        2,
        cv2.LINE_AA,
    )

    cv2.putText(
        panel,
        f"{dominant_probability:.1f}%",
        (235, 74),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.72,
        (235, 235, 235),
        2,
        cv2.LINE_AA,
    )

    # Linha separadora
    cv2.line(
        panel,
        (20, 90),
        (PANEL_WIDTH - 20, 90),
        (75, 75, 75),
        1,
    )

    label_x = 20
    bar_x = 108
    bar_width = PANEL_WIDTH - bar_x - 52
    bar_height = 20

    initial_y = 112
    spacing = 46

    for index, emotion_name in enumerate(
        EMOTION_NAMES
    ):
        probability = float(
            emotions.get(emotion_name, 0.0)
        )

        probability = max(
            0.0,
            min(100.0, probability),
        )

        current_y = initial_y + index * spacing

        # Nome da emoção
        cv2.putText(
            panel,
            emotion_name.upper(),
            (label_x, current_y + 15),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.42,
            (215, 215, 215),
            1,
            cv2.LINE_AA,
        )

        # Fundo da barra
        cv2.rectangle(
            panel,
            (bar_x, current_y),
            (bar_x + bar_width, current_y + bar_height),
            (65, 65, 65),
            -1,
        )

        # Parte preenchida
        filled_width = int(
            bar_width * probability / 100.0
        )

        emotion_color = EMOTION_COLORS.get(
            emotion_name,
            (160, 160, 160),
        )

        if filled_width > 0:
            cv2.rectangle(
                panel,
                (bar_x, current_y),
                (
                    bar_x + filled_width,
                    current_y + bar_height,
                ),
                emotion_color,
                -1,
            )

        # Borda
        cv2.rectangle(
            panel,
            (bar_x, current_y),
            (bar_x + bar_width, current_y + bar_height),
            (110, 110, 110),
            1,
        )

        # Percentual
        percentage_text = f"{probability:5.1f}%"

        cv2.putText(
            panel,
            percentage_text,
            (
                bar_x + bar_width + 6,
                current_y + 15,
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.40,
            (225, 225, 225),
            1,
            cv2.LINE_AA,
        )

    # FPS
    fps_y = frame_height - 42

    cv2.line(
        panel,
        (20, fps_y - 22),
        (PANEL_WIDTH - 20, fps_y - 22),
        (75, 75, 75),
        1,
    )

    cv2.putText(
        panel,
        f"FPS DA INTERFACE: {fps:.1f}",
        (22, fps_y),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.48,
        (180, 180, 180),
        1,
        cv2.LINE_AA,
    )

    cv2.putText(
        panel,
        "Q ou ESC para sair",
        (22, frame_height - 14),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.42,
        (150, 150, 150),
        1,
        cv2.LINE_AA,
    )

    return panel


def normalize_region(region):
    """
    Garante que a região tenha apenas valores inteiros.
    """

    if not region:
        return None

    return {
        "x": int(region.get("x", 0)),
        "y": int(region.get("y", 0)),
        "w": int(region.get("w", 0)),
        "h": int(region.get("h", 0)),
    }


# ============================================================
# INICIALIZAÇÃO
# ============================================================

stabilizer = EmotionStabilizer(
    EMOTION_NAMES,
    alpha=SMOOTHING_ALPHA,
)

cap = cv2.VideoCapture(
    CAMERA_INDEX,
    cv2.CAP_V4L2,
)

# Fallback caso CAP_V4L2 não funcione
if not cap.isOpened():
    cap.release()
    cap = cv2.VideoCapture(CAMERA_INDEX)

# Tenta usar MJPG antes de configurar a resolução
cap.set(
    cv2.CAP_PROP_FOURCC,
    cv2.VideoWriter_fourcc(*"MJPG"),
)

cap.set(
    cv2.CAP_PROP_FRAME_WIDTH,
    CAMERA_WIDTH,
)

cap.set(
    cv2.CAP_PROP_FRAME_HEIGHT,
    CAMERA_HEIGHT,
)

cap.set(
    cv2.CAP_PROP_BUFFERSIZE,
    1,
)

if not cap.isOpened():
    raise RuntimeError(
        "Não foi possível abrir a webcam."
    )


cv2.namedWindow(
    WINDOW_NAME,
    cv2.WINDOW_NORMAL,
)

# Dimensões iniciais da janela completa
cv2.resizeWindow(
    WINDOW_NAME,
    CAMERA_WIDTH + PANEL_WIDTH,
    CAMERA_HEIGHT,
)


# ============================================================
# VARIÁVEIS DE EXECUÇÃO
# ============================================================

frame_counter = 0

last_region = None

stabilized_emotions = {
    emotion: 0.0
    for emotion in EMOTION_NAMES
}

previous_time = time.perf_counter()
fps = 0.0

print("Iniciando análise.")
print("Pressione Q ou ESC para sair.")


# ============================================================
# LOOP PRINCIPAL
# ============================================================

try:
    while True:
        success, frame = cap.read()

        if not success:
            print(
                "Não foi possível capturar "
                "a imagem da webcam."
            )
            break

        frame_counter += 1

        should_analyze = (
            frame_counter % ANALYSIS_INTERVAL == 0
        )

        if should_analyze:
            try:
                results = DeepFace.analyze(
                    img_path=frame,
                    actions=["emotion"],
                    enforce_detection=False,
                    detector_backend="yunet",
                    silent=True,
                )

                result = get_first_result(results)

                if result is not None:
                    raw_emotions = result.get(
                        "emotion",
                        {},
                    )

                    region = result.get(
                        "region",
                        None,
                    )

                    if raw_emotions:
                        stabilized_emotions = (
                            stabilizer.update(
                                raw_emotions
                            )
                        )

                    normalized_region = normalize_region(
                        region
                    )

                    if normalized_region is not None:
                        last_region = normalized_region

            except Exception as analysis_error:
                print(
                    "Erro durante a análise: "
                    f"{analysis_error}"
                )

        # Desenha a última região detectada
        if last_region is not None:
            draw_face_information(
                frame,
                last_region,
                stabilized_emotions,
            )

        # Calcula o FPS da interface
        current_time = time.perf_counter()

        elapsed = current_time - previous_time

        if elapsed > 0:
            instantaneous_fps = 1.0 / elapsed

            # Pequena suavização do FPS exibido
            fps = (
                0.90 * fps
                + 0.10 * instantaneous_fps
            )

        previous_time = current_time

        # Cria o painel lateral
        panel = draw_emotion_panel(
            frame_height=frame.shape[0],
            emotions=stabilized_emotions,
            fps=fps,
        )

        # Junta webcam e painel em uma única imagem
        interface = np.hstack(
            (
                frame,
                panel,
            )
        )

        cv2.imshow(
            WINDOW_NAME,
            interface,
        )

        key = cv2.waitKey(1) & 0xFF

        if key in (
            ord("q"),
            ord("Q"),
            27,
        ):
            break

        # Encerra caso a janela seja fechada
        if cv2.getWindowProperty(
            WINDOW_NAME,
            cv2.WND_PROP_VISIBLE,
        ) < 1:
            break

finally:
    cap.release()
    cv2.destroyAllWindows()

    print("Programa encerrado.")