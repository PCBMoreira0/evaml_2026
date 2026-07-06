import time

from rich.progress import Progress, TextColumn, BarColumn, TimeElapsedColumn



def node_processing(node, memory, client_mqtt):
    """ Função de tratamento do nó """

    duration = node.attrib["duration"]
    
    seconds = int(duration)/1000

    # Tempo em segundos
    tempo_total = int(seconds)

    # Barra de progresso personalizada
    with Progress(
        TextColumn("[b white]State:[/] [b white]Waiting [/]for [b white]" + str(seconds) + "[/] seconds. 🕒"),
        BarColumn(bar_width=20),
        TextColumn("[bold cyan]{task.fields[tempo]}")
    ) as progress:
        
        # Adicionar tarefa
        task = progress.add_task("", total=tempo_total, tempo="--:--")
        
        # Contagem regressiva
        for segundos_restantes in range(tempo_total, -1, -1):
            # Formatar o tempo restante
            minutos = segundos_restantes // 60
            segundos = segundos_restantes % 60
            tempo_str = f"{minutos:02d}:{segundos:02d}"
            
            # Atualizar a barra e o campo de tempo
            progresso_atual = tempo_total - segundos_restantes
            progress.update(task, completed=progresso_atual, tempo=tempo_str)
            
            # Aguardar 1 segundo, mas apenas se não for o último valor
            if segundos_restantes > 0:
                time.sleep(1)

    return node # It returns the same node