import subprocess

scripts = [
    "robot_package/sim_components/sim_audio/sim_audio.py",
    "robot_package/sim_components/sim_eva_robot/sim_eva_robot.py",
    "robot_package/sim_components/sim_light/sim_light.py",
    "robot_package/sim_components/sim_tts_msg/sim_tts_msg.py"
]

processes = []

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