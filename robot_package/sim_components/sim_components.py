import subprocess

scripts = [
    "robot_package/sim_components/sim_audio/sim_audio.py",
    "robot_package/sim_components/sim_light/sim_light.py",
    # "robot_package/sim_components/sim_tts_msg/sim_tts_msg.py"
    # "robot_package/sim_components/sim_tts_kokoro/sim_tts_kokoro.py"
    "robot_package/sim_components/sim_tts_piper/sim_tts_piper.py"
]

processes = []

# Inicia o processo do FRED virtual (Específico aqui porque ele é um executável)
# s = "robot_package/sim_components/sim_fred_robot/sim_fred_robot"
# print(f"Iniciando {s}...")
# p = subprocess.Popen([s])
# processes.append(p)

for s in scripts:
    print(f"Iniciando {s}...")
    p = subprocess.Popen(["python3", s])
    processes.append(p)


try:
    # execução normal
    for p in processes:
        p.wait()
except KeyboardInterrupt:
    print("Encerrando todos os subprocessos...")
    for p in processes:
        p.terminate()
