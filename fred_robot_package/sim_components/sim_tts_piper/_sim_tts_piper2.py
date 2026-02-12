import wave
from piper.voice import PiperVoice
import numpy as np
import io
import soundfile as sf
import librosa  # pip install librosa

# Carrega modelo
PiperVoice.load("pt_BR-faber-medium.onnx", "pt_BR-faber-medium.onnx.json")


text = "Isso é muito bom! Agora, tenho uma voz mais parecida com uma criança."

# Gera áudio em buffer (ao invés de arquivo direto)
buffer = io.BytesIO()
with wave.open(buffer, "wb") as wav_file:
    wav_file.setnchannels(1)
    wav_file.setsampwidth(2)
    wav_file.setframerate(voice.config.sample_rate)
    voice.synthesize(text, wav_file)

# Converte para NumPy
buffer.seek(0)
with wave.open(buffer, "rb") as wav_file:
    frames = wav_file.readframes(-1)
    audio_array = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0

# APLICA PITCH SHIFTING
semitons = 6  # +4 semitons = mais agudo (voz de criança)
audio_pitched = librosa.effects.pitch_shift(audio_array, sr=voice.config.sample_rate, n_steps=semitons)


# Salva resultado
sf.write("output.wav", audio_pitched, voice.config.sample_rate)
print("✓ Áudio com pitch alterado salvo!")