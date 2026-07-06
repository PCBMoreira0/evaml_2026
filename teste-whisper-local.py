# import os
# # Força o PyTorch a ignorar a GPU e usar a CPU globalmente antes de qualquer importação
# os.environ["CUDA_VISIBLE_DEVICES"] = ""

import speech_recognition as sr
import warnings

# Remove os alertas visuais do PyTorch sobre o driver antigo
warnings.filterwarnings("ignore")

r = sr.Recognizer()

with sr.Microphone() as source:
    print("\n--- Pode falar! Estou ouvindo... ---")
    audio = r.listen(source)
    print("Áudio capturado! Processando transcrição...")

try:
    # Removemos o device="cpu" daqui, pois a linha 'os.environ' lá em cima já resolveu
    #texto = r.recognize_whisper(audio, model="base", language="portuguese") #   para processamento local
    texto = r.recognize_google(audio, language = "pt-BR")
    print("\nTranscrição:")
    print(texto)

except Exception as e:
    print(f"Ocorreu um erro: {e}")