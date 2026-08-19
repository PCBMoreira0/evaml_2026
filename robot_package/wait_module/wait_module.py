import time

from rich.progress import Progress, TextColumn, BarColumn, TimeElapsedColumn

from base_command_handler import BaseCommandHandler

class CommandHandler(BaseCommandHandler):

    def __init__(self, xml_node, communicator_obj):
        
        super().__init__(self, communicator_obj)

    def node_process(self, xml_node, memory):
        """ Node handling function """

        duration = xml_node.attrib["duration"]

        duration_ms = int(duration)  # duração em milissegundos

        intervalo = 100  # atualização a cada 100 ms
        total_passos = duration_ms // intervalo

        with Progress(
            TextColumn(f"[b white]State:[/] [b white]Waiting[/] for [b white]{duration_ms}[/] ms. 🕒"),
            BarColumn(bar_width=20),
            TextColumn("[bold cyan]{task.fields[tempo]}")
        ) as progress:
        
            task = progress.add_task("", total=total_passos, tempo="00:00.000")
        
            for restante in range(duration_ms, -1, -intervalo):
                minutos = restante // 60000
                segundos = (restante % 60000) // 1000
                milissegundos = restante % 1000
        
                tempo_str = f"{minutos:02d}:{segundos:02d}.{milissegundos:03d}"
        
                progresso = (duration_ms - restante) // intervalo
                progress.update(task, completed=progresso, tempo=tempo_str)
        
                if restante > 0:
                    time.sleep(intervalo / 1000)
        
        return xml_node # It returns the same node