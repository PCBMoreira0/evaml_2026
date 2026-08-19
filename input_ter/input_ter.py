import os
import sys
import json
import time

from pathlib import Path
from threading import Lock

from paho.mqtt import client as mqtt_client
from transformers import pipeline


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
    os.getcwd() + "/robot_package/"
)

import robot_package.robot_profile as robot_profile


# ============================================================
# CONFIGURAÇÕES DE AMBIENTE
# ============================================================

os.environ["QT_LOGGING_RULES"] = (
    "*.debug=false;"
    "*.warning=false;"
    "qt.qpa.fonts=false"
)

import matplotlib

matplotlib.rcParams["toolbar"] = "None"

import matplotlib.pyplot as plt


# ============================================================
# CONFIGURAÇÕES MQTT
# ============================================================

broker = config.MQTT_BROKER_ADRESS
port = config.MQTT_PORT

robot_base_topic = robot_profile.ROBOT_BASE_TOPIC

PERCEPTION_TOPIC = (
    robot_base_topic + "/PERCEPTION"
)

TER_TEXT_TOPIC = (
    robot_base_topic + "/TER_TEXT"
)

PULSE_INPUT_TOPIC = (
    robot_base_topic + "/PULSE/INPUT"
)


# ============================================================
# CONFIGURAÇÕES DAS EMOÇÕES
# ============================================================

# Nomes utilizados internamente pelo sistema.
EMOTION_NAMES = [
    "anger",
    "disgust",
    "fear",
    "happiness",
    "sadness",
    "surprise",
    "neutral",
]

# Nomes exibidos na interface.
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

# Conversão dos nomes retornados pelo modelo para os nomes
# utilizados pelo framework.
MODEL_LABEL_MAPPING = {
    "anger": "anger",
    "angry": "anger",
    "disgust": "disgust",
    "fear": "fear",
    "joy": "happiness",
    "happy": "happiness",
    "happiness": "happiness",
    "sad": "sadness",
    "sadness": "sadness",
    "surprise": "surprise",
    "neutral": "neutral",
}


# ============================================================
# VARIÁVEIS COMPARTILHADAS
# ============================================================

result_to_pulse = json.dumps({})

list_sources_to_receive = []

current_text = (
    "Waiting for a sentence..."
)

current_probabilities = {
    emotion: 0.0
    for emotion in EMOTION_NAMES
}

# Indica que existem novos dados para atualizar a GUI.
gui_update_pending = False

# Protege os dados compartilhados entre a thread MQTT
# e a thread principal do Matplotlib.
data_lock = Lock()


# ============================================================
# CARREGAMENTO DO MODELO
# ============================================================

print(
    "Carregando o modelo de IA "
    "(Emotion Classifier)... Aguarde."
)

classifier = pipeline(
    "sentiment-analysis",
    model="michellejieli/emotion_text_classifier",
    top_k=None,
)

print(
    "Modelo 'michellejieli/emotion_text_classifier' "
    "carregado com sucesso!"
)


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def normalize_classifier_result(result):
    """
    Padroniza os nomes das emoções retornadas pelo modelo
    e garante que todas as sete emoções estejam presentes.
    """

    probabilities = {
        emotion: 0.0
        for emotion in EMOTION_NAMES
    }

    for item in result:
        original_label = str(
            item.get("label", "")
        ).lower()

        standardized_label = (
            MODEL_LABEL_MAPPING.get(
                original_label
            )
        )

        if standardized_label is None:
            print(
                "Rótulo não reconhecido:",
                original_label,
            )
            continue

        probabilities[standardized_label] = float(
            item.get("score", 0.0)
        )

    # Corrige pequenas diferenças numéricas na soma
    # das probabilidades.
    total = sum(
        probabilities.values()
    )

    if total > 0:
        probabilities = {
            emotion: probability / total
            for emotion, probability
            in probabilities.items()
        }

    return probabilities


def get_dominant_emotion(probabilities):
    """
    Retorna a emoção dominante e sua probabilidade.
    """

    if not probabilities:
        return "neutral", 0.0

    dominant_emotion = max(
        probabilities,
        key=probabilities.get,
    )

    dominant_probability = float(
        probabilities[dominant_emotion]
    )

    return (
        dominant_emotion,
        dominant_probability,
    )


def get_emotion_label(emotion_name):
    """
    Converte o nome interno da emoção para o nome
    exibido na interface.
    """

    emotion_mapping = dict(
        zip(
            EMOTION_NAMES,
            EMOTION_LABELS,
        )
    )

    return emotion_mapping.get(
        emotion_name,
        emotion_name.capitalize(),
    )


def prepare_sentence_for_gui(
    sentence,
    maximum_length=100,
):
    """
    Limita frases longas para que caibam na interface
    estreita sem alterar o texto utilizado na classificação.
    """

    sentence = sentence.strip()

    if len(sentence) <= maximum_length:
        return sentence

    return (
        sentence[:maximum_length - 3]
        + "..."
    )


# ============================================================
# MQTT
# ============================================================

def on_connect(client, userdata, flags, rc):
    """
    Callback executado quando o cliente se conecta
    ao broker MQTT.
    """

    if rc == 0:
        client.subscribe(
            topic=[
                (PERCEPTION_TOPIC, 1),
                (TER_TEXT_TOPIC, 1),
            ]
        )

        print(
            "Input TER Module - Connected."
        )

        print(
            "PERCEPTION topic:",
            PERCEPTION_TOPIC,
        )

        print(
            "TER_TEXT topic:",
            TER_TEXT_TOPIC,
        )

    else:
        print(
            "Falha na conexão MQTT. Código:",
            rc,
        )


def on_message(client, userdata, msg):
    """
    Callback executado quando uma mensagem MQTT é recebida.
    """

    global result_to_pulse
    global list_sources_to_receive
    global current_text
    global current_probabilities
    global gui_update_pending

    # --------------------------------------------------------
    # CONTROLE DA JANELA DE PERCEPÇÃO
    # --------------------------------------------------------

    if msg.topic == PERCEPTION_TOPIC:
        try:
            message = json.loads(
                msg.payload.decode("utf-8")
            )

        except (
            json.JSONDecodeError,
            UnicodeDecodeError,
        ) as error:
            print(
                "Mensagem PERCEPTION inválida:",
                error,
            )
            return

        action = str(
            message.get("action", "")
        ).upper()

        if action == "START":
            list_sources_to_receive = (
                message.get("sources", [])
            )

            print(
                "Lista de fontes:",
                list_sources_to_receive,
            )

        elif action == "END":
            print(
                "Lista de fontes no END:",
                list_sources_to_receive,
            )

            if "TER" in list_sources_to_receive:
                client.publish(
                    PULSE_INPUT_TOPIC,
                    result_to_pulse,
                )

                print(
                    "Resultado TER enviado ao PULSE:",
                    result_to_pulse,
                )

                list_sources_to_receive = []

                print(
                    "Lista de fontes zerada."
                )

        else:
            print(
                "Ação PERCEPTION desconhecida:",
                action,
            )

        return

    # --------------------------------------------------------
    # CLASSIFICAÇÃO DO TEXTO
    # --------------------------------------------------------

    if msg.topic == TER_TEXT_TOPIC:
        try:
            received_text = msg.payload.decode(
                "utf-8"
            ).strip()

        except UnicodeDecodeError as error:
            print(
                "Não foi possível decodificar o texto:",
                error,
            )
            return

        if not received_text:
            print(
                "Uma mensagem de texto vazia foi recebida."
            )
            return

        print(
            "Frase recebida:",
            received_text,
        )

        try:
            start_time = time.perf_counter()

            classifier_output = classifier(
                received_text
            )

            elapsed_time = (
                time.perf_counter()
                - start_time
            )

            print(
                "Tempo de classificação: "
                f"{elapsed_time * 1000:.2f} ms"
            )

            if (
                not classifier_output
                or not isinstance(
                    classifier_output,
                    list,
                )
            ):
                print(
                    "O classificador retornou "
                    "um resultado inválido."
                )
                return

            # Algumas versões do Transformers retornam:
            #
            # [[
            #   {"label": "joy", "score": ...},
            #   ...
            # ]]
            #
            # Outras podem retornar diretamente:
            #
            # [
            #   {"label": "joy", "score": ...},
            #   ...
            # ]

            if isinstance(
                classifier_output[0],
                list,
            ):
                classifier_result = (
                    classifier_output[0]
                )

            else:
                classifier_result = (
                    classifier_output
                )

            probabilities = (
                normalize_classifier_result(
                    classifier_result
                )
            )

            result = {
                "source": "TER",
                "representation": "CAT",
                "probabilities": probabilities,
            }

            result_to_pulse = json.dumps(
                result
            )

            print(
                "Resultado TER:",
                result_to_pulse,
            )

            print(
                "Soma das probabilidades:",
                sum(probabilities.values()),
            )

            # O callback MQTT não altera diretamente
            # os elementos do Matplotlib.
            with data_lock:
                current_text = received_text

                current_probabilities = (
                    probabilities.copy()
                )

                gui_update_pending = True

        except Exception as classification_error:
            print(
                "Erro durante a classificação:",
                classification_error,
            )


# ============================================================
# INICIALIZAÇÃO DA GUI
# ============================================================

plt.ion()

# Aproximadamente 240 × 280 pixels considerando DPI=100.
# Mantém a altura da versão anterior e reduz a largura
# pela metade.
fig, ax = plt.subplots(
    figsize=(4.2, 2.8)
)

try:
    fig.canvas.manager.set_window_title(
        "Text Emotion Recognition (TER) - Input Module"
    )

except AttributeError:
    pass


# ------------------------------------------------------------
# FRASE ANALISADA
# ------------------------------------------------------------

sentence_label = fig.text(
    0.04,
    0.965,
    "Sentence:",
    ha="left",
    va="top",
    fontsize=8,
    fontweight="bold",
)

sentence_text = fig.text(
    0.04,
    0.905,
    "Waiting for a sentence...",
    ha="left",
    va="top",
    fontsize=8,
    wrap=True,
)


# ------------------------------------------------------------
# GRÁFICO DE BARRAS
# ------------------------------------------------------------

bars = ax.barh(
    EMOTION_LABELS,
    [0.0] * len(EMOTION_LABELS),
    color=EMOTION_COLORS,
    edgecolor="black",
    linewidth=0.4,
    height=0.55,
)

ax.set_xlim(
    0,
    100,
)

ax.set_xlabel(
    "Probability (%)",
    fontsize=7.5,
    labelpad=1,
)

ax.set_title(
    "Waiting for text...",
    fontsize=9,
    fontweight="bold",
    pad=3,
)

ax.tick_params(
    axis="x",
    labelsize=7,
    pad=1,
)

ax.tick_params(
    axis="y",
    labelsize=7.5,
    pad=1,
)

ax.grid(
    axis="x",
    linestyle="--",
    linewidth=0.4,
    alpha=0.3,
)

ax.invert_yaxis()

ax.margins(
    y=0.03
)

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

# A margem esquerda precisa ser maior devido aos nomes
# Happiness e Surprise.
fig.subplots_adjust(
    left=0.35,
    right=0.97,
    top=0.72,
    bottom=0.16,
)

fig.show()


# ============================================================
# ATUALIZAÇÃO DA GUI
# ============================================================

def update_gui(
    sentence,
    probabilities,
):
    """
    Atualiza a frase, as barras, os percentuais
    e a emoção dominante.
    """

    sentence_text.set_text(
        prepare_sentence_for_gui(
            sentence
        )
    )

    for index, emotion_name in enumerate(
        EMOTION_NAMES
    ):
        probability = float(
            probabilities.get(
                emotion_name,
                0.0,
            )
        )

        percentage = (
            probability * 100.0
        )

        bars[index].set_width(
            percentage
        )

        # Em valores menores, o percentual aparece
        # depois do final da barra.
        #
        # Em valores maiores, aparece dentro da barra
        # para não ultrapassar o limite do gráfico.
        if percentage < 72:
            text_x = percentage + 2
            horizontal_alignment = "left"

        else:
            text_x = percentage - 2
            horizontal_alignment = "right"

        percentage_texts[index].set_x(
            text_x
        )

        percentage_texts[index].set_ha(
            horizontal_alignment
        )

        percentage_texts[index].set_text(
            f"{percentage:.1f}%"
        )

    dominant_emotion, dominant_probability = (
        get_dominant_emotion(
            probabilities
        )
    )

    dominant_label = get_emotion_label(
        dominant_emotion
    )

    ax.set_title(
        (
            f"{dominant_label}: "
            f"{dominant_probability * 100:.1f}%"
        ),
        fontsize=9,
        fontweight="bold",
        pad=3,
    )

    fig.canvas.draw_idle()
    fig.canvas.flush_events()


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

    plt.close("all")

    sys.exit(1)

# O MQTT é executado em uma thread separada para que
# a interface gráfica continue responsiva.
client.loop_start()


# ============================================================
# LOOP PRINCIPAL DA GUI
# ============================================================

print(
    "Interface TER iniciada."
)

print(
    "Feche a janela para encerrar."
)

try:
    while plt.fignum_exists(
        fig.number
    ):
        sentence_to_display = None
        probabilities_to_display = None

        with data_lock:
            if gui_update_pending:
                sentence_to_display = (
                    current_text
                )

                probabilities_to_display = (
                    current_probabilities.copy()
                )

                gui_update_pending = False

        if (
            sentence_to_display is not None
            and probabilities_to_display is not None
        ):
            update_gui(
                sentence_to_display,
                probabilities_to_display,
            )

        # Mantém a GUI responsiva.
        plt.pause(1)


# ============================================================
# FINALIZAÇÃO
# ============================================================

finally:
    client.loop_stop()
    client.disconnect()

    plt.close("all")

    print(
        "Programa encerrado."
    )