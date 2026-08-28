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

app = Flask(__name__)
engine = None


def node_info(node):
    if node is None:
        return None
    return {"tag": node.tag, "text": (node.text or "").strip()[:80], "id": node.get("id")}


def result(executed=None, error=None):
    upcoming = node_info(getattr(engine, "node", None)) if engine else None
    return jsonify({
        "state": engine.get_state() if engine else "NO_SCRIPT",
        "executed": executed,   # o nó que acabou de rodar (None se nada rodou nesta chamada)
        "upcoming": upcoming,   # o nó que vai rodar na próxima vez que "avançar" for clicado
        "history": engine.history_size() if engine else 0,
        "log": log.drain(),
        "error": error,
    })


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/scripts")
def list_scripts():
    try:
        files = sorted(f for f in os.listdir(SCRIPTS_DIR) if f.endswith(".xml"))
    except OSError:
        files = []
    return jsonify({"scripts": files})


@app.post("/api/load")
def load():
    global engine
    engine = ScriptEngine()
    if not engine.load_script(os.path.join(SCRIPTS_DIR, request.json["script_file"])):
        engine = None
        return result(error="Não foi possível ler o arquivo.")
    engine.initialize()
    return result()


@app.post("/api/start")
def start():
    engine.start_script(request.json.get("mode", "simulator"))
    return result()


@app.post("/api/step")
def step():
    executed = node_info(engine.node)
    engine.play_next()
    return result(executed=executed)


@app.post("/api/repeat")
def repeat():
    if not engine.previous():
        return result(error="Não há comando anterior para repetir.")
    executed = node_info(engine.node)
    engine.play_next()
    return result(executed=executed)


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


@app.errorhandler(Exception)
def on_error(exc):
    return result(error=type(exc).__name__ + ": " + str(exc))


if __name__ == "__main__":
    # threaded=True: enquanto um <listen> bloqueia o /api/step, o /api/input precisa ser atendido.
    app.run(port=5000, threaded=True, use_reloader=False)