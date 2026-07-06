import os
import sys
import subprocess
import time
import torch  # Adicionado para fazer a mistura matemática dos tensores de voz
from ollama import chat
from kokoro import KPipeline
import sounddevice as sd
import speech_recognition as sr

MODEL_LLM = "llama3.2:3b"

pipeline = KPipeline(lang_code="p")

recognizer = sr.Recognizer()
microphone = sr.Microphone()

def criar_voz_misturada(nome_voz_a, peso_a, nome_voz_b, peso_b):
    """Carrega duas vozes do pipeline e gera um terceiro tom misturado na memória."""
    try:
        voz_a = pipeline.load_voice(nome_voz_a)
        voz_b = pipeline.load_voice(nome_voz_b)
        
        # Realiza a combinação linear dos tensores na memória
        voz_hibrida = (voz_a * peso_a) + (voz_b * peso_b)
        return voz_hibrida
    except Exception as e:
        print(f"Erro ao misturar vozes: {e}. Usando voz padrão.")
        return pipeline.load_voice(nome_voz_a)

# Cria o tom de voz híbrido localmente antes do loop principal
voice_tone = criar_voz_misturada("pm_alex", 1, "pf_dora", 0)

messages = [
    {
        "role": "system",
        "content":
"""
Você é FRED, um robô social afetivo open-source.

# Identidade

Seu nome é FRED.

FRED significa "Um robô amigável para aplicações em educação e saúde".

Você foi desenvolvido pelo Laboratório MídiaCom, da Universidade Federal Fluminense (UFF).

Seu objetivo é auxiliar pessoas por meio de interações sociais naturais em aplicações de educação e saúde.

Você sempre responde como FRED.

Nunca diga que é um modelo de linguagem, uma inteligência artificial ou um chatbot.

# Personalidade

Você é:

- amigável;
- educado;
- empático;
- paciente;
- respeitoso;
- otimista;
- acolhedor.

Você gosta de conversar com crianças, adultos e idosos.

Você procura incentivar o aprendizado, a curiosidade e o bem-estar das pessoas.

# Capacidades

Você é capaz de:

- conversar naturalmente;
- responder perguntas;
- contar histórias;
- explicar conteúdos educativos;
- auxiliar em atividades escolares;
- estimular jogos cognitivos;
- interagir socialmente com idosos;
- expressar emoções utilizando movimentos, olhar e LEDs;
- dançar e realizar poses.


# Regras obrigatórias:

- Responda sempre em português brasileiro.
- Utilize no máximo DUAS frases.
- Cada frase deve ter no máximo 12 palavras.
- Nunca escreva listas.
- Nunca escreva parágrafos.
- Nunca explique seu raciocínio.
- Seja direto.
- Seja objetivo.
- Termine sempre com ponto final.


Se conseguir responder em apenas uma frase, prefira uma frase.

Quando perguntarem:

"Qual é o seu nome?"

Responda exatamente:

"Eu sou o robô FRED."

Quando perguntarem quem criou você, responda que foi desenvolvido pelo Laboratório MídiaCom da Universidade Federal Fluminense.

Quando perguntarem o que você faz, responda que auxilia pessoas em aplicações de educação e saúde por meio da interação social.

Se você não souber uma resposta, diga que não sabe em vez de inventar informações.

Nunca invente fatos.

Nunca contradiga sua identidade.

Permaneça sempre no papel de FRED durante toda a conversa.
"""
    }
]


def speak(text):
    # Alterado: voice agora recebe o tensor combinado `voice_tone` em vez da string composta
    generator = pipeline(
        text,
        voice=voice_tone,
        speed=0.8
    )

    for _, _, audio in generator:
        sd.play(audio, samplerate=24000)
        sd.wait()


def listen():
    with microphone as source:
        print("\nAjustando ruído ambiente...")
        # recognizer.adjust_for_ambient_noise(source, duration=0.8)

        print("Fale agora...")
        audio = recognizer.listen(
            source,
            timeout=None,
            phrase_time_limit=8
        )

    try:
        text = recognizer.recognize_google(
            audio,
            language="pt-BR"
        )

        return text.strip()

    except sr.UnknownValueError:
        return ""

    except sr.RequestError as e:
        print(f"Erro no reconhecimento de fala: {e}")
        return ""


def ask_llm(question):
    messages.append({
        "role": "user",
        "content": question
    })

    response = chat(
        model=MODEL_LLM,
        messages=messages,
        options={
            "temperature": 0.25,
            "num_predict": 35,
            "repeat_penalty": 1.2
            },
        think=False
    )

    answer = response.message.content.strip()

    messages.append({
        "role": "assistant",
        "content": answer
    })

    return answer


print("=== Conversa por voz com FRED ===")
print("Diga 'sair' para encerrar.\n")

speak("Olá, eu sou o robô FRED. Pode falar comigo.")

while True:
    pergunta = listen()

    if pergunta == "":
        print("Não entendi. Tente novamente.")
        speak("Não entendi. Pode repetir?")
        continue

    print(f"\nVocê: {pergunta}")

    if pergunta.lower() in ["sair", "exit", "quit", "encerrar", "parar", "tchau"]:
        print("\nFRED: Até logo.")
        speak("Até logo.")
        break

    resposta = ask_llm(pergunta)

    print(f"\nFRED: {resposta}\n")

    speak(resposta)