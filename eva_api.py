# EVA Script Engine - API Flask
#
# Coloque este arquivo na mesma pasta do script_engine.py.
#   pip install flask
#   python eva_api.py   ->   http://127.0.0.1:5000

import os
import queue
import sys
import threading

from flask import Flask, jsonify, render_template, request

SCRIPTS_DIR = "eva_scripts"


# Captura a saída do rich para mostrar na página (e continua imprimindo no terminal).
class LogCapture:
    def __init__(self, mirror):
        self.mirror, self.lines, self.buf = mirror, [], ""
        self.lock = threading.Lock()

    def write(self, text):
        self.mirror.write(text)
        with self.lock:
            self.buf += text
            while "\n" in self.buf:
                line, self.buf = self.buf.split("\n", 1)
                self.lines.append(line)

    def flush(self):
        self.mirror.flush()

    def isatty(self):
        return False

    def drain(self):
        with self.lock:
            lines, self.lines = self.lines, []
            return lines


# stdin alimentado pela página: o console.input() do <listen> espera aqui.
class WebStdin:
    def __init__(self):
        self.q = queue.Queue()

    def readline(self, *args):
        return self.q.get() + "\n"

    def isatty(self):
        return False


log = LogCapture(sys.stdout)
web_stdin = WebStdin()
sys.stdout = log
sys.stdin = web_stdin

from script_engine import ScriptEngine  # importado após a troca do stdout
from log_collector import LogCollector

app = Flask(__name__)
engine = None
mode = None
collector = None


def node_info(node):
    if node is None:
        return None
    return {"tag": node.tag, "text": (node.text or "").strip()[:80], "id": node.get("id")}


def result(error=None):
    # previous  -> penúltimo nó executado
    # current   -> último nó executado (é o que "Repetir" reexecuta)
    # upcoming  -> nó apontado pelo cursor (é o que "Avançar" executa)
    return jsonify({
        "state": engine.get_state() if engine else "NO_SCRIPT",
        "mode": mode,
        "previous": node_info(engine.executed_node(1)) if engine else None,
        "current": node_info(engine.executed_node(0)) if engine else None,
        "upcoming": node_info(getattr(engine, "node", None)) if engine else None,
        "history": engine.history_size() if engine else 0,
        "log": log.drain(),
        "collector": collector.status() if collector else {"running": False, "logs": []},
        "error": error,
    })


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/scripts")
def list_scripts():
    try:
        files = sorted(f for f in os.listdir(SCRIPTS_DIR)
                       if f.endswith(".xml") and "_evaml" in f)
    except OSError:
        files = []
    return jsonify({"scripts": files})


@app.post("/api/load")
def load():
    global engine, mode
    engine = ScriptEngine()
    mode = None
    if not engine.load_script(os.path.join(SCRIPTS_DIR, request.json["script_file"])):
        engine = None
        return result(error="Não foi possível ler o arquivo.")
    engine.initialize()
    return result()


@app.post("/api/start")
def start():
    global mode
    mode = request.json.get("mode", "terminal")
    # Descarta entradas digitadas que sobraram de uma execução anterior.
    while not web_stdin.q.empty():
        web_stdin.q.get_nowait()
    engine.start_script(mode)
    return result()


@app.post("/api/step")
def step():
    engine.play_next()
    return result()


@app.post("/api/repeat")
def repeat():
    if not engine.previous():
        return result(error="Não há comando para repetir.")
    engine.play_next()
    return result()


@app.post("/api/back")
def back():
    if not engine.previous():
        return result(error="Não há histórico para voltar.")
    return result()


@app.post("/api/reset")
def reset():
    engine.reset()
    return result()


@app.post("/api/input")
def send_input():
    web_stdin.q.put(request.json.get("text", ""))
    return jsonify({"ok": True})


def resolve_dir(raw):
    """Aceita caminho relativo ao projeto, absoluto ou com '~'."""
    return os.path.abspath(os.path.expanduser(raw or "logs"))


@app.get("/api/log/path")
def log_path():
    """Resolve o caminho digitado, para a interface mostrar onde vai gravar."""
    path = resolve_dir(request.args.get("dir"))
    exists = os.path.isdir(path)
    # Se ainda não existe, o que importa é poder escrever na pasta-mãe existente
    # mais próxima, que é onde o makedirs vai atuar.
    probe = path
    while not os.path.isdir(probe) and os.path.dirname(probe) != probe:
        probe = os.path.dirname(probe)
    return jsonify({
        "path": path,
        "exists": exists,
        "writable": os.access(probe, os.W_OK),
        "csv": len([f for f in os.listdir(path) if f.endswith(".csv")]) if exists else 0,
    })


@app.get("/api/log/status")
def log_status():
    return jsonify(collector.status() if collector else {"running": False, "logs": []})


@app.post("/api/log/start")
def log_start():
    global collector
    if collector and collector.running:
        collector.stop()
    try:
        collector = LogCollector(output_dir=resolve_dir(request.json.get("output_dir")))
        collector.start()
    except Exception as exc:
        collector = None
        return jsonify({"running": False, "logs": [],
                        "error": type(exc).__name__ + ": " + str(exc)})
    return jsonify(collector.status())


@app.post("/api/log/stop")
def log_stop():
    if collector:
        collector.stop()
    return jsonify(collector.status() if collector else {"running": False, "logs": []})


@app.errorhandler(Exception)
def on_error(exc):
    return result(error=type(exc).__name__ + ": " + str(exc))


if __name__ == "__main__":
    # threaded=True: enquanto um <listen> bloqueia o /api/step, o /api/input precisa ser atendido.
    app.run(port=5000, threaded=True, use_reloader=False)