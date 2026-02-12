import time

from rich.progress import Progress, TextColumn, BarColumn, TimeElapsedColumn

from base_command_handler import BaseCommandHandler

class CommandHandler(BaseCommandHandler):

    def __init__(self, xml_node, communicator_obj):
        
        super().__init__(self, communicator_obj)

    def node_process(self, xml_node, memory):
        """ Node handling function """

        duration = xml_node.attrib["duration"]

        seconds = int(duration)

        # Time in seconds
        tempo_total = int(seconds)

        # Barra de progresso personalizada
        with Progress(
            TextColumn("[b white]State:[/] [b white]Waiting [/]for [b white]" + str(seconds) + "[/] seconds. 🕒"),
            BarColumn(bar_width=20),
            TextColumn("[bold cyan]{task.fields[tempo]}")
        ) as progress:
            
            # Adicionar tarefa
            task = progress.add_task("", total=tempo_total, tempo="--:--")
            
            # Countdown
            for segundos_restantes in range(tempo_total, -1, -1):
                # Format the remaining time
                minutos = segundos_restantes // 60
                segundos = segundos_restantes % 60
                tempo_str = f"{minutos:02d}:{segundos:02d}"
                
                # Update the bar and time field
                progresso_atual = tempo_total - segundos_restantes
                progress.update(task, completed=progresso_atual, tempo=tempo_str)
                
                # Wait 1 second, but only if it is not the last value
                if segundos_restantes > 0:
                    time.sleep(1)

        return xml_node # It returns the same node