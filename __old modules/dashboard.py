from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.live import Live
from rich.layout import Layout
from rich import box
import time
import random

# Função para gerar conteúdo de log que cresce com o tempo
def generate_log_content(existing_logs=None, max_lines=1000):
    if existing_logs is None:
        existing_logs = []
    
    # Criar algumas novas linhas de log
    log_types = ["INFO", "WARNING", "ERROR", "DEBUG"]
    services = ["API", "Database", "Authentication", "Frontend", "Cache"]
    messages = [
        "Request processed",
        "Connection established",
        "Timeout occurred",
        "Data validation failed",
        "Cache invalidated",
        "User logged in",
        "Config reloaded",
        "Memory usage high",
        "Service restarted"
    ]
    
    timestamp = time.strftime("%H:%M:%S")
    log_type = random.choice(log_types)
    service = random.choice(services)
    message = random.choice(messages)
    
    # Formatar a linha de log com cor baseada no tipo
    color = {
        "INFO": "blue",
        "WARNING": "yellow",
        "ERROR": "red",
        "DEBUG": "green"
    }.get(log_type, "white")
    
    new_log = f"{timestamp} [{color}]{log_type}[/] [{service}] {message}"
    
    # Adicionar à lista existente
    existing_logs.append(new_log)
    
    # Limitar ao número máximo de linhas (manter as mais recentes)
    if len(existing_logs) > max_lines:
        existing_logs = existing_logs[-max_lines:]
    
    return existing_logs

def create_manual_scrollable_panel(content, title, visible_lines=10):
    # Apenas mostrar as últimas X linhas (simulando rolagem)
    visible_content = content[-visible_lines:]
    
    # Criar um texto formatado com as linhas visíveis
    text = Text("\n".join(visible_content))
    
    # Adicionar indicação de mais conteúdo disponível
    total_lines = len(content)
    hidden_lines = max(0, total_lines - visible_lines)
    
    title_with_count = f"{title} ({visible_lines} de {total_lines} linhas visíveis)"
    
    # Criar o painel sem overflow
    panel = Panel(
        text,
        title=title_with_count,
        subtitle=f"↑ {hidden_lines} linhas anteriores não visíveis ↑" if hidden_lines > 0 else None,
        box=box.ROUNDED,
        border_style="blue"
    )
    
    return panel

# Configurar o layout
def make_layout():
    layout = Layout()
    
    layout.split(
        Layout(name="header", size=3),
        Layout(name="main"),
        Layout(name="footer", size=3)
    )
    
    # Dividir a área principal em duas colunas
    layout["main"].split_row(
        Layout(name="logs", ratio=2),
        Layout(name="stats", ratio=1)
    )
    
    # Adicionar conteúdo ao cabeçalho e rodapé
    layout["header"].update(Panel(
        Text("DASHBOARD COM PAINEL ROLÁVEL SIMULADO", style="bold white", justify="center"),
        style="blue"
    ))
    
    layout["footer"].update(Panel(
        Text("Pressione Ctrl+C para sair | Mostrando últimas 10 linhas de logs", 
             style="italic white", justify="center"),
        style="blue"
    ))
    
    return layout

# Inicializar logs
logs = []
for _ in range(20):  # Começar com 20 logs para mostrar o comportamento de rolagem
    logs = generate_log_content(logs)

# Criar o console e o layout
console = Console()
layout = make_layout()

# Executar a atualização ao vivo
try:
    with Live(layout, refresh_per_second=1, screen=True):
        while True:
            # Gerar novos logs
            logs = generate_log_content(logs)
            
            # Atualizar o painel com rolagem manual
            layout["logs"].update(
                create_manual_scrollable_panel(logs, "📜 Logs do Sistema", visible_lines=10)
            )
            
            # Atualizar estatísticas
            log_types = {
                "INFO": sum(1 for log in logs if "[blue]INFO[/]" in log),
                "WARNING": sum(1 for log in logs if "[yellow]WARNING[/]" in log),
                "ERROR": sum(1 for log in logs if "[red]ERROR[/]" in log),
                "DEBUG": sum(1 for log in logs if "[green]DEBUG[/]" in log)
            }
            
            stats_text = Text()
            stats_text.append(f"Total de logs: {len(logs)}\n")
            stats_text.append(f"INFO: {log_types['INFO']}\n")
            stats_text.append(f"WARNING: {log_types['WARNING']}\n")
            stats_text.append(f"ERROR: {log_types['ERROR']}\n")
            stats_text.append(f"DEBUG: {log_types['DEBUG']}\n\n")
            stats_text.append(f"Última atualização: {time.strftime('%H:%M:%S')}")
            
            layout["stats"].update(
                Panel(
                    stats_text,
                    title="📊 Estatísticas",
                    border_style="green"
                )
            )
            
            time.sleep(1)
except KeyboardInterrupt:
    console.print("[bold green]Dashboard encerrado![/bold green]")