import os
import sys
import json
import time

from pathlib import Path
from statistics import median

from paho.mqtt import client as mqtt_client


# ============================================================
# DIRETÓRIOS E MÓDULOS DO ROBÔ
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

parent_dir = os.path.abspath(
    os.path.join(BASE_DIR, "../")
)

sys.path.append(parent_dir)

import config

sys.path.append(
    os.getcwd() + "/" + "robot_package/"
)

import robot_profile


# ============================================================
# CONFIGURAÇÕES MQTT E VARIÁVEIS GLOBAIS
# ============================================================

broker = config.MQTT_BROKER_ADRESS
port = config.MQTT_PORT

robot_base_topic = robot_profile.ROBOT_BASE_TOPIC

result_to_pulse = json.dumps({})

# Define se o FER está classificando e armazenando observações.
active = False

# Fontes que devem produzir resultados na janela de percepção.
list_sources_to_receive = []

# Lista com as classificações produzidas na janela atual.
observation_list = []

# Solicita que a thread principal limpe o gráfico.
clear_chart_requested = False

# Resultado final normalizado que será apresentado no gráfico.
# Os valores são armazenados em porcentagem, no intervalo [0, 100].
final_emotions_to_display = None

# Indica que há um resultado final aguardando apresentação.
final_chart_update_requested = False


# ============================================================
# CONFIGURAÇÕES DE AMBIENTE
# ============================================================

# Configurações feitas antes de importar TensorFlow e DeepFace.
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

os.environ["QT_LOGGING_RULES"] = (
    "*.debug=false;"
    "*.warning=false;"
    "qt.qpa.fonts=false"
)

import matplotlib

matplotlib.rcParams["toolbar"] = "None"

import cv2
import matplotlib.pyplot as plt

from deepface import DeepFace


# ============================================================
# CONFIGURAÇÕES DO FER
# ============================================================

CAMERA_INDEX = 1

CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480

DISPLAY_WIDTH = 480
DISPLAY_HEIGHT = 360

# Executa o DeepFace a cada N frames.
ANALYSIS_INTERVAL = 5

# Quanto maior, mais estável e mais lenta é a resposta.
SMOOTHING_ALPHA = 0.65

WINDOW_NAME = (
    "Input Module - FER - Camera View"
)

# Nomes usados internamente pelo DeepFace.
EMOTION_NAMES = [
    "angry",
    "disgust",
    "fear",
    "happy",
    "sad",
    "surprise",
    "neutral",
]

# Nomes mostrados na janela do gráfico.
EMOTION_LABELS = [
    "Anger",
    "Disgust",
    "Fear",
    "Happiness",
    "Sadness",
    "Surprise",
    "Neutral",
]

EMOTION_COLORS = [
    "crimson",
    "saddlebrown",
    "purple",
    "green",
    "royalblue",
    "gold",
    "gray",
]


# ============================================================
# MQTT
# ============================================================

def on_connect(client, userdata, flags, rc):
    """
    Callback executado quando o módulo se conecta ao broker.
    """

    perception_topic = (
        robot_base_topic + "/PERCEPTION"
    )

    client.subscribe(
        topic=[
            (perception_topic, 1),
        ]
    )

    print(
        "Input FER Module - Connected.",
        perception_topic,
    )


def on_message(client, userdata, msg):
    """
    Callback executado quando uma mensagem MQTT é recebida.
    """

    global result_to_pulse
    global list_sources_to_receive
    global active
    global observation_list
    global clear_chart_requested
    global final_emotions_to_display
    global final_chart_update_requested

    perception_topic = (
        robot_base_topic + "/PERCEPTION"
    )

    if msg.topic != perception_topic:
        return

    try:
        message = json.loads(
            msg.payload.decode()
        )

    except (
        json.JSONDecodeError,
        UnicodeDecodeError,
    ) as error:
        print(
            "Mensagem inválida recebida em PERCEPTION:",
            error,
        )
        return

    action = message.get(
        "action",
        "",
    ).upper()

    # --------------------------------------------------------
    # INÍCIO DA JANELA DE PERCEPÇÃO
    # --------------------------------------------------------

    if action == "START":
        list_sources_to_receive = message.get(
            "sources",
            [],
        )

        if "FER" in list_sources_to_receive:
            # Limpa possíveis observações de uma janela anterior.
            observation_list = []

            # Descarta o resultado final anterior.
            final_emotions_to_display = None
            final_chart_update_requested = False

            # Solicita que a thread principal limpe o gráfico.
            clear_chart_requested = True

            active = True

            print("Classificação iniciada...")

        return

    # --------------------------------------------------------
    # FIM DA JANELA DE PERCEPÇÃO
    # --------------------------------------------------------

    if action == "END":
        if "FER" not in list_sources_to_receive:
            return

        active = False

        print("Classificação encerrada...")

        print(
            "Número de observações:",
            len(observation_list),
        )

        # Evita executar median() sobre listas vazias.
        if not observation_list:
            print(
                "Nenhuma observação FER foi coletada "
                "durante a janela de percepção."
            )

            list_sources_to_receive = []
            observation_list = []

            final_emotions_to_display = None
            final_chart_update_requested = False

            return

        angry_list = []
        disgust_list = []
        fear_list = []
        happy_list = []
        sad_list = []
        surprise_list = []
        neutral_list = []

        for observation in observation_list:
            angry_list.append(
                float(
                    observation.get(
                        "angry",
                        0.0,
                    )
                )
            )

            disgust_list.append(
                float(
                    observation.get(
                        "disgust",
                        0.0,
                    )
                )
            )

            fear_list.append(
                float(
                    observation.get(
                        "fear",
                        0.0,
                    )
                )
            )

            happy_list.append(
                float(
                    observation.get(
                        "happy",
                        0.0,
                    )
                )
            )

            sad_list.append(
                float(
                    observation.get(
                        "sad",
                        0.0,
                    )
                )
            )

            surprise_list.append(
                float(
                    observation.get(
                        "surprise",
                        0.0,
                    )
                )
            )

            neutral_list.append(
                float(
                    observation.get(
                        "neutral",
                        0.0,
                    )
                )
            )

        # O DeepFace retorna os valores em porcentagem.
        # A divisão por 100 converte para o intervalo [0, 1].
        probabilities = {
            "neutral": (
                float(median(neutral_list)) / 100.0
            ),
            "sadness": (
                float(median(sad_list)) / 100.0
            ),
            "surprise": (
                float(median(surprise_list)) / 100.0
            ),
            "fear": (
                float(median(fear_list)) / 100.0
            ),
            "anger": (
                float(median(angry_list)) / 100.0
            ),
            "disgust": (
                float(median(disgust_list)) / 100.0
            ),
            "happiness": (
                float(median(happy_list)) / 100.0
            ),
        }

        # As medianas são calculadas separadamente.
        # Portanto, a soma pode ser diferente de 1.
        total = sum(
            probabilities.values()
        )

        if total > 0:
            probabilities = {
                emotion: probability / total
                for emotion, probability
                in probabilities.items()
            }

        # ----------------------------------------------------
        # RESULTADO PARA O PULSE
        # ----------------------------------------------------

        result_to_pulse = {
            "source": "FER",
            "representation": "CAT",
            "probabilities": probabilities,
        }

        result_to_pulse = json.dumps(
            result_to_pulse
        )

        print(
            "Result to PULSE:",
            result_to_pulse,
        )

        print(
            "Soma das probabilidades:",
            sum(probabilities.values()),
        )

        client.publish(
            robot_base_topic + "/PULSE/INPUT",
            result_to_pulse,
        )

        # ----------------------------------------------------
        # RESULTADO FINAL PARA O GRÁFICO
        # ----------------------------------------------------
        #
        # O gráfico utiliza os nomes internos do DeepFace:
        #
        # angry, disgust, fear, happy, sad, surprise, neutral
        #
        # O JSON enviado ao PULSE utiliza:
        #
        # anger, disgust, fear, happiness, sadness,
        # surprise, neutral
        #
        # As probabilidades são exatamente as mesmas enviadas
        # ao PULSE, multiplicadas por 100 para apresentação
        # no gráfico.

        final_emotions_to_display = {
            "angry": (
                probabilities.get(
                    "anger",
                    0.0,
                ) * 100.0
            ),
            "disgust": (
                probabilities.get(
                    "disgust",
                    0.0,
                ) * 100.0
            ),
            "fear": (
                probabilities.get(
                    "fear",
                    0.0,
                ) * 100.0
            ),
            "happy": (
                probabilities.get(
                    "happiness",
                    0.0,
                ) * 100.0
            ),
            "sad": (
                probabilities.get(
                    "sadness",
                    0.0,
                ) * 100.0
            ),
            "surprise": (
                probabilities.get(
                    "surprise",
                    0.0,
                ) * 100.0
            ),
            "neutral": (
                probabilities.get(
                    "neutral",
                    0.0,
                ) * 100.0
            ),
        }

        # A atualização do Matplotlib será realizada
        # pela thread principal.
        final_chart_update_requested = True

        # Limpa os dados da janela encerrada.
        list_sources_to_receive = []
        observation_list = []

        return

    print(
        "Ação de percepção desconhecida:",
        action,
    )


# ============================================================
# ESTABILIZAÇÃO DAS PROBABILIDADES
# ============================================================

class EmotionStabilizer:
    def __init__(
        self,
        emotion_names,
        alpha=0.85,
    ):
        if not 0 <= alpha < 1:
            raise ValueError(
                "alpha deve estar no intervalo [0, 1)."
            )

        self.alpha = alpha

        self.values = {
            emotion: 0.0
            for emotion in emotion_names
        }

        self.initialized = False

    def update(self, emotions):
        if not self.initialized:
            for emotion in self.values:
                self.values[emotion] = float(
                    emotions.get(
                        emotion,
                        0.0,
                    )
                )

            self.initialized = True

        else:
            for emotion in self.values:
                current_value = float(
                    emotions.get(
                        emotion,
                        0.0,
                    )
                )

                previous_value = (
                    self.values[emotion]
                )

                self.values[emotion] = (
                    self.alpha * previous_value
                    + (
                        1.0 - self.alpha
                    ) * current_value
                )

        return self.values.copy()

    def get_current(self):
        return self.values.copy()

    def reset(self):
        """
        Zera o estado interno do estabilizador.
        """

        self.values = {
            emotion: 0.0
            for emotion in self.values
        }

        self.initialized = False


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def get_first_result(results):
    """
    A saída do DeepFace normalmente é uma lista.
    Esta função também trata o retorno como dicionário.
    """

    if isinstance(results, list):
        if not results:
            return None

        return results[0]

    if isinstance(results, dict):
        return results

    return None


def get_dominant_emotion(emotions):
    """
    Retorna a emoção dominante e seu percentual.
    """

    if not emotions:
        return "neutral", 0.0

    dominant_emotion = max(
        emotions,
        key=emotions.get,
    )

    probability = float(
        emotions[dominant_emotion]
    )

    return dominant_emotion, probability


def get_emotion_label(emotion_name):
    """
    Converte o nome interno do DeepFace para o nome
    exibido na interface.
    """

    emotion_labels = {
        "angry": "Anger",
        "disgust": "Disgust",
        "fear": "Fear",
        "happy": "Happiness",
        "sad": "Sadness",
        "surprise": "Surprise",
        "neutral": "Neutral",
    }

    return emotion_labels.get(
        emotion_name,
        emotion_name.capitalize(),
    )


def update_emotion_chart(
    ax,
    bars,
    percentage_texts,
    emotions,
    final_result=False,
):
    """
    Atualiza as barras e os percentuais do gráfico.

    final_result=False:
        apresenta a classificação instantânea estabilizada.

    final_result=True:
        apresenta o resultado final das medianas normalizadas.
    """

    for index, emotion_name in enumerate(
        EMOTION_NAMES
    ):
        probability = float(
            emotions.get(
                emotion_name,
                0.0,
            )
        )

        bars[index].set_width(
            probability
        )

        if probability < 88:
            text_x = probability + 1
            horizontal_alignment = "left"

        else:
            text_x = probability - 1
            horizontal_alignment = "right"

        percentage_texts[index].set_x(
            text_x
        )

        percentage_texts[index].set_ha(
            horizontal_alignment
        )

        percentage_texts[index].set_text(
            f"{probability:.1f}%"
        )

    dominant_emotion, dominant_probability = (
        get_dominant_emotion(emotions)
    )

    dominant_label = get_emotion_label(
        dominant_emotion
    )

    if final_result:
        title = (
            f"{dominant_label.upper()}: "
            f"{dominant_probability:.1f}%"
        )

    else:
        title = (
            f"{dominant_label.upper()}: "
            f"{dominant_probability:.1f}%"
        )

    ax.set_title(
        title,
        fontsize=10,
    )


def clear_emotion_chart(
    ax,
    bars,
    percentage_texts,
):
    """
    Zera todas as barras e os textos do gráfico.
    """

    for bar in bars:
        bar.set_width(0.0)

    for percentage_text in percentage_texts:
        percentage_text.set_x(1)
        percentage_text.set_ha("left")
        percentage_text.set_text("0.0%")

    ax.set_title(
        " ",
        fontsize=10,
    )


def draw_face_information(
    frame,
    region,
    emotions,
):
    """
    Desenha o retângulo e o texto da emoção sobre o frame.
    """

    frame_height, frame_width = (
        frame.shape[:2]
    )

    x = max(
        0,
        int(
            region.get(
                "x",
                0,
            )
        ),
    )

    y = max(
        0,
        int(
            region.get(
                "y",
                0,
            )
        ),
    )

    width = max(
        0,
        int(
            region.get(
                "w",
                0,
            )
        ),
    )

    height = max(
        0,
        int(
            region.get(
                "h",
                0,
            )
        ),
    )

    x2 = min(
        frame_width - 1,
        x + width,
    )

    y2 = min(
        frame_height - 1,
        y + height,
    )

    dominant_emotion, probability = (
        get_dominant_emotion(emotions)
    )

    dominant_label = get_emotion_label(
        dominant_emotion
    )

    cv2.rectangle(
        frame,
        (x, y),
        (x2, y2),
        (0, 255, 0),
        2,
    )

    label = (
        f"{dominant_label.upper()}: "
        f"{probability:.1f}%"
    )

    text_y = max(
        y - 10,
        25,
    )

    cv2.putText(
        frame,
        label,
        (x, text_y),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (0, 255, 0),
        2,
        cv2.LINE_AA,
    )


# ============================================================
# INICIALIZAÇÃO DO GRÁFICO
# ============================================================

plt.ion()

fig, ax = plt.subplots(
    figsize=(4, 2.7)
)

try:
    fig.canvas.manager.set_window_title(
        "Input Module - FER - Emotion Probabilities"
    )
except AttributeError:
    pass


bars = ax.barh(
    EMOTION_LABELS,
    [0.0] * len(EMOTION_LABELS),
    color=EMOTION_COLORS,
    edgecolor="black",
    height=0.65,
)

ax.set_xlim(
    0,
    100,
)

ax.set_xlabel(
    "Probability (%)",
    fontsize=8,
)

ax.set_title(
    " ",
    fontsize=10,
)

ax.tick_params(
    axis="x",
    labelsize=7,
)

ax.tick_params(
    axis="y",
    labelsize=8,
)

ax.grid(
    axis="x",
    linestyle="--",
    alpha=0.3,
)

ax.invert_yaxis()

percentage_texts = []

for bar in bars:
    percentage_text = ax.text(
        1,
        bar.get_y()
        + bar.get_height() / 2,
        "0.0%",
        va="center",
        ha="left",
        fontsize=7,
    )

    percentage_texts.append(
        percentage_text
    )

fig.tight_layout()
fig.show()


# ============================================================
# INICIALIZAÇÃO DA WEBCAM
# ============================================================

cap = cv2.VideoCapture(
    CAMERA_INDEX,
    cv2.CAP_V4L2,
)

# Caso CAP_V4L2 não funcione no sistema.
if not cap.isOpened():
    cap.release()

    cap = cv2.VideoCapture(
        CAMERA_INDEX
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

# O formato MJPG pode melhorar o desempenho
# de determinadas webcams.
cap.set(
    cv2.CAP_PROP_FOURCC,
    cv2.VideoWriter_fourcc(*"MJPG"),
)

if not cap.isOpened():
    plt.close("all")

    raise RuntimeError(
        "Não foi possível abrir a webcam."
    )


# Janela redimensionável.
cv2.namedWindow(
    WINDOW_NAME,
    cv2.WINDOW_NORMAL,
)

cv2.resizeWindow(
    WINDOW_NAME,
    DISPLAY_WIDTH,
    DISPLAY_HEIGHT,
)


# ============================================================
# INICIALIZAÇÃO DOS OBJETOS DE EXECUÇÃO
# ============================================================

stabilizer = EmotionStabilizer(
    EMOTION_NAMES,
    alpha=SMOOTHING_ALPHA,
)

frame_counter = 0

last_region = None
stabilized_emotions = None

# Armazena o valor anterior de active para detectar
# a transição de True para False.
previous_active = active

print("Iniciando análise.")
print("Pressione Q ou ESC para sair.")


# ============================================================
# INICIALIZAÇÃO DO CLIENTE MQTT
# ============================================================

client = mqtt_client.Client()

client.on_connect = on_connect
client.on_message = on_message

try:
    client.connect(
        broker,
        port,
    )

except Exception as connection_error:
    print(
        "Unable to connect to Broker:",
        connection_error,
    )

    cap.release()
    cv2.destroyAllWindows()
    plt.close("all")

    sys.exit(1)

# loop_start executa o MQTT em uma thread separada,
# permitindo manter as interfaces gráficas responsivas.
client.loop_start()


# ============================================================
# EXECUÇÃO PRINCIPAL
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

        # ----------------------------------------------------
        # LIMPEZA NO INÍCIO DA CLASSIFICAÇÃO
        # ----------------------------------------------------
        #
        # O callback MQTT apenas solicita a limpeza.
        # O Matplotlib é manipulado na thread principal.

        if clear_chart_requested:
            clear_emotion_chart(
                ax,
                bars,
                percentage_texts,
            )

            last_region = None
            stabilized_emotions = None

            stabilizer.reset()

            fig.canvas.draw_idle()
            fig.canvas.flush_events()

            clear_chart_requested = False

        # ----------------------------------------------------
        # DETECTA O ENCERRAMENTO DA CLASSIFICAÇÃO
        # ----------------------------------------------------
        #
        # Ao encerrar, remove apenas as informações visuais
        # instantâneas da webcam. O gráfico não é apagado.

        if previous_active and not active:
            last_region = None
            stabilized_emotions = None

            stabilizer.reset()

        previous_active = active

        # ----------------------------------------------------
        # APRESENTAÇÃO DO RESULTADO FINAL
        # ----------------------------------------------------
        #
        # O resultado final foi calculado no callback MQTT,
        # mas é apresentado aqui para evitar atualizar o
        # Matplotlib em uma thread secundária.

        if (
            final_chart_update_requested
            and final_emotions_to_display is not None
        ):
            update_emotion_chart(
                ax,
                bars,
                percentage_texts,
                final_emotions_to_display,
                final_result=True,
            )

            fig.canvas.draw_idle()
            fig.canvas.flush_events()

            final_chart_update_requested = False

        frame_counter += 1

        # DeepFace somente a cada N frames e quando o módulo
        # estiver ativo.
        should_analyze = (
            frame_counter
            % ANALYSIS_INTERVAL
            == 0
            and active
        )

        if should_analyze:
            print("Classificando...")

            try:
                start_time = (
                    time.perf_counter()
                )

                results = DeepFace.analyze(
                    img_path=frame,
                    actions=["emotion"],
                    enforce_detection=False,
                    detector_backend="yunet",
                    silent=True,
                )

                elapsed_time = (
                    time.perf_counter()
                    - start_time
                )

                print(
                    "Tempo do frame: "
                    f"{elapsed_time * 1000:.2f} ms"
                )

                result = get_first_result(
                    results
                )

                if result is not None:
                    raw_emotions = result.get(
                        "emotion",
                        {},
                    )

                    # Armazena uma cópia com floats nativos.
                    observation = {
                        emotion: float(
                            raw_emotions.get(
                                emotion,
                                0.0,
                            )
                        )
                        for emotion in EMOTION_NAMES
                    }

                    observation_list.append(
                        observation
                    )

                    print(
                        type(observation),
                        observation,
                    )

                    last_region = result.get(
                        "region",
                        None,
                    )

                    stabilized_emotions = (
                        stabilizer.update(
                            raw_emotions
                        )
                    )

                    update_emotion_chart(
                        ax,
                        bars,
                        percentage_texts,
                        stabilized_emotions,
                        final_result=False,
                    )

                    fig.canvas.draw_idle()
                    fig.canvas.flush_events()

            except Exception as analysis_error:
                print(
                    "Erro durante a análise: "
                    f"{analysis_error}"
                )

        # ----------------------------------------------------
        # DESENHO DO RETÂNGULO VERDE
        # ----------------------------------------------------
        #
        # O retângulo somente é desenhado quando active=True.

        if (
            active
            and last_region is not None
            and stabilized_emotions is not None
        ):
            draw_face_information(
                frame,
                last_region,
                stabilized_emotions,
            )

        cv2.imshow(
            WINDOW_NAME,
            frame,
        )

        # Mantém o Matplotlib responsivo.
        plt.pause(0.001)

        key = cv2.waitKey(1) & 0xFF

        if key in (
            ord("q"),
            ord("Q"),
            27,
        ):
            break

        # Encerra caso a janela da webcam seja fechada.
        if cv2.getWindowProperty(
            WINDOW_NAME,
            cv2.WND_PROP_VISIBLE,
        ) < 1:
            break

        # Encerra caso a janela do gráfico seja fechada.
        if not plt.fignum_exists(
            fig.number
        ):
            break


# ============================================================
# FINALIZAÇÃO
# ============================================================

finally:
    client.loop_stop()
    client.disconnect()

    cap.release()

    cv2.destroyAllWindows()
    plt.close("all")

    print("Programa encerrado.")