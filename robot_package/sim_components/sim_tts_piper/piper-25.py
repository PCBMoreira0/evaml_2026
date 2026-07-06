import wave
from piper import PiperVoice

voice = PiperVoice.load("pt_BR-faber-medium.onnx")


with wave.open("test.wav", "wb") as wav_file:
    voice.synthesize_wav("Olá, meu nome é Fréde! Bem vindo ao mundo da síntese de voz!", wav_file)


