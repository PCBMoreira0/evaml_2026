# Coletor de logs EVA: escuta as mensagens MQTT de <log> e grava um CSV por log.
#
# Uso independente da interface (continua funcionando como antes):
#     python log_collector.py                 # grava na pasta atual
#     python log_collector.py logs_da_sessao  # grava na pasta indicada
#
# Uso embarcado (é o que a API Flask faz):
#     c = LogCollector(output_dir="logs")
#     c.start()   # conecta e escuta numa thread de fundo
#     c.stop()    # desconecta e fecha as linhas pendentes

import csv
import os
import sys

import paho.mqtt.client as mqtt

# Enviado como conteúdo de um <log> para indicar "fim de linha": a linha atual
# do CSV é fechada e gravada, e uma nova começa na próxima mensagem.
LINE_BREAK_SYMBOL = "§"

# Enviado para indicar que aquele log terminou de mandar dados.
END_SYMBOL = "~"

BROKER_IP = "localhost"
BROKER_PORT = 1883
TOPIC = "TERMINAL/LOG"


class LogCollector:
    def __init__(self, output_dir=".", broker=BROKER_IP, port=BROKER_PORT,
                 topic=TOPIC, stop_when_finished=False):
        # stop_when_finished=True reproduz o comportamento do script original:
        # desconecta quando todos os logs vistos enviaram "~". Embarcado na API
        # o padrão é False, para continuar gravando na próxima execução do script.
        # Aceita caminho relativo, absoluto ou com "~" (fora do projeto, inclusive).
        self.output_dir = os.path.abspath(os.path.expanduser(output_dir))
        self.broker, self.port, self.topic = broker, port, topic
        self.stop_when_finished = stop_when_finished

        self.row_buffers = {}      # log_name -> colunas da linha em construção
        self.last_timestamps = {}  # log_name -> timestamp da última coluna
        self.log_states = {}       # log_name -> "active" | "finished"
        self.row_counts = {}       # log_name -> linhas já gravadas
        self.running = False
        self.client = None

    # -- CSV --
    def csv_path(self, log_name):
        return os.path.join(self.output_dir, log_name + ".csv")

    def flush_row(self, log_name):
        """Grava a linha em construção no CSV do log_name e limpa o buffer."""
        row = self.row_buffers.get(log_name)
        if not row:
            return

        full_row = row + [self.last_timestamps.get(log_name, "")]
        path = self.csv_path(log_name)
        file_exists = os.path.exists(path)

        os.makedirs(self.output_dir, exist_ok=True)
        with open(path, "a", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["col%d" % (i + 1) for i in range(len(row))] + ["timestamp"])
            writer.writerow(full_row)

        self.row_counts[log_name] = self.row_counts.get(log_name, 0) + 1
        print("Linha gravada para log '%s' em '%s': %s" % (log_name, path, full_row))
        self.row_buffers[log_name] = []
        self.last_timestamps[log_name] = ""

    def append_to_row(self, log_name, text, timestamp):
        self.row_buffers.setdefault(log_name, []).append(text)
        self.last_timestamps[log_name] = timestamp

    # -- MQTT --
    def on_connect(self, client, userdata, flags, rc, properties=None):
        print("Conectado ao broker com código %s" % rc)
        client.subscribe(self.topic)

    def on_message(self, client, userdata, msg):
        payload = msg.payload.decode().strip()
        print("[%s] Mensagem recebida: %s" % (msg.topic, payload))

        # Formato esperado: logname_seq_texto|timestamp
        parts = payload.split("_", 2)
        if len(parts) < 3:
            print("Formato inválido. Esperado: logname_seq_texto|timestamp")
            return

        log_name, seq, rest = parts

        # Trata "~" mesmo que venha sem o "|timestamp"
        stripped = rest.strip()
        if stripped == END_SYMBOL or stripped.split("|", 1)[0] == END_SYMBOL:
            print("Comando '%s' recebido do log '%s'." % (END_SYMBOL, log_name))
            self.flush_row(log_name)
            self.log_states[log_name] = "finished"
            if self.stop_when_finished and self.log_states and \
               all(s == "finished" for s in self.log_states.values()):
                print("Todos os logs enviaram '~'. Encerrando...")
                client.disconnect()
            return

        if "|" not in rest:
            print("Timestamp não encontrado na mensagem, ignorando.")
            return

        text, timestamp = rest.rsplit("|", 1)

        if log_name not in self.log_states:
            self.log_states[log_name] = "active"

        if text.strip() == LINE_BREAK_SYMBOL:
            self.flush_row(log_name)
            return

        self.append_to_row(log_name, text, timestamp)

    # -- Controle --
    def _make_client(self):
        client = mqtt.Client()
        client.on_connect = self.on_connect
        client.on_message = self.on_message
        print("Conectando ao broker MQTT em %s:%s ..." % (self.broker, self.port))
        client.connect(self.broker, self.port)
        return client

    def start(self):
        """Conecta e passa a escutar numa thread de fundo."""
        if self.running:
            return
        os.makedirs(self.output_dir, exist_ok=True)
        self.client = self._make_client()
        self.client.loop_start()
        self.running = True

    def stop(self):
        """Fecha as linhas pendentes e desconecta."""
        if not self.running:
            return
        for log_name in list(self.row_buffers):
            self.flush_row(log_name)
        self.client.loop_stop()
        self.client.disconnect()
        self.running = False

    def run_forever(self):
        """Modo script: bloqueia até o broker desconectar."""
        os.makedirs(self.output_dir, exist_ok=True)
        self.client = self._make_client()
        self.running = True
        self.client.loop_forever()
        self.running = False

    def status(self):
        return {
            "running": self.running,
            "output_dir": self.output_dir,
            "topic": self.topic,
            "logs": [
                {"name": name,
                 "state": self.log_states[name],
                 "rows": self.row_counts.get(name, 0),
                 "pending": len(self.row_buffers.get(name, []))}
                for name in sorted(self.log_states)
            ],
        }


if __name__ == "__main__":
    output_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    LogCollector(output_dir=output_dir, stop_when_finished=True).run_forever()