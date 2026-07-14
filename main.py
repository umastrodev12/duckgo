from duckgo.global_dir import globalDir
from duckgo.groq.ai_client import AIClient
from duckgo.tools import write_file, WRITE_TOOL
from duckgo.command_reader import (
    cmd_clear,
    cmd_help,
    cmd_read,
    cmd_write,
)
from rich.markdown import Markdown
from rich.panel import Panel
from rich.align import Align
from rich.text import Text
from rich.console import Console
import datetime
import getpass
import time
import os

console = Console()

LOGO = """
██████╗ ██╗   ██╗ ██████╗██╗  ██╗     ██████╗  ██████╗ 
██╔══██╗██║   ██║██╔════╝██║ ██╔╝    ██╔════╝ ██╔═══██╗
██║  ██║██║   ██║██║     █████╔╝     ██║  ███╗██║   ██║
██║  ██║██║   ██║██║     ██╔═██╗     ██║   ██║██║   ██║
██████╔╝╚██████╔╝╚██████╗██║  ██╗    ╚██████╔╝╚██████╔╝
╚═════╝  ╚═════╝  ╚═════╝╚═╝  ╚═╝     ╚═════╝  ╚═════╝
"""

COMMANDS = {
    "/read": cmd_read,
    "/help": cmd_help,
    "/write": cmd_write,
}

TOOLS = [WRITE_TOOL]
TOOL_FUNCTIONS = {
    "write_file": write_file,
}

SYSTEM_PROMPT = """Você é o Duck AI, um assistente pessoal de programação.
Seja direto e técnico. Você também pode responder dúvidas simples.
Sua língua fluente é Português Brasileiro.

Você roda dentro de um terminal chamado Duck Go, que tem os seguintes comandos disponíveis para o usuário:
- /read <arquivo> - lê e envia o conteúdo de um arquivo do projeto para você analisar
- /write <arquivo> - escreve ou sobescreve um arquivo que o usuário pedir
- /clear - limpa o histórico da conversa atual
- /help - mostra a lista de comandos

Se o usuário perguntar sobre como usar você, ou pedir para analisar um arquivo sem ter usado o /read ainda, sugira que ele use o comando /read <arquivo>."""

def parse_command(prompt: str, ai) -> str | None:
    """Retorna o texto a enviar pra IA, ou None se o comando já foi tratado sozinho."""
    parts = prompt.strip().split()
    cmd = parts[0]
    args = parts[1:]

    if cmd == "/clear":
        return cmd_clear(args, ai)

    handler = COMMANDS.get(cmd)
    if handler:
        return handler(args)

    console.print(f"[red]Comando desconhecido: {cmd}[/red]")
    return None

def ensure_api_key(duck) -> str:
    config = duck.load_config()
    key = config.get("groq_api_key")

    if not key:
        console.print("[yellow]Nenhuma API key da Groq encontrada.[/yellow]")
        key = console.input("[bold]Cole sua GROQ_API_KEY: [/bold]").strip()
        config["groq_api_key"] = key
        duck.save_config(config)
        console.print("[green]Chave salva![/green]")

    return key

def show_menu():
    console.print(Align.center(Text(LOGO, style="bold yellow")))

    
    menu_text = Text()
    menu_text.append("1", style="bold cyan")
    menu_text.append(". Iniciar Duck AI\n", style="white")
    menu_text.append("2", style="bold red")
    menu_text.append(". Sair", style="white")

    panel = Panel(
        menu_text,
        title="[bold]Selecione uma opção[/bold]",
        border_style="yellow",
        padding=(1, 4),
        expand=False,
    )

    console.print(Align.center(panel))
    console.print()


def get_greeting() -> str:
    hour = datetime.datetime.now().hour
    if hour < 12:
        return "Bom dia"
    elif hour < 18:
        return "Boa tarde"
    return "Boa noite"


def show_welcome(duck_dir, model: str):
    usuario = getpass.getuser()

    greeting = get_greeting()
    cwd = os.path.basename(os.getcwd())
    body = Text()
    body = Text()
    body.append(f"{greeting}, {usuario} 🦆\n\n", style="bold")
    body.append(f"Diretório: ", style="dim")
    body.append(f"{cwd}\n", style="cyan")
    body.append(f"Modelo: ", style="dim")
    body.append(f"{model}\n\n", style="yellow")
    body.append("Dicas:\n", style="bold dim")
    body.append("  /read <arquivo>  ", style="green")
    body.append("- analisa um arquivo do projeto\n", style="dim")
    body.append("  sair              ", style="red")
    body.append("- encerra a sessão\n", style="dim")

    panel = Panel(
        body,
        title="[bold yellow]🦆 Duck Go[/bold yellow]",
        border_style="yellow",
        padding=(1, 3),
        expand=False,
    )

    console.print(Align.center(panel))

def main():
    global ai

    duck = globalDir.findGlobalDuck()
    if duck is None:
        duck = globalDir(os.getcwd())
        duck.createGlobalDuck()

    ai = AIClient(model=duck.get_model())

    # flags
    isAIinitialized: bool = False
    ai = None

    while True:
        if not isAIinitialized:
            show_welcome(duck, model=duck.get_model())

            prompt = console.input("> ").strip()

            if prompt.startswith("iniciar chat"):
                console.print("[bold green] Iniciando Chat...[/bold green]")
                time.sleep(2)
                ai = AIClient(model=duck.get_model())
                isAIinitialized = True

            if prompt.lower() in ("sair", "exit", "quit"):
                break

            if not prompt:
                console.print("[red] Algo deu errado. [/red]")
        

        prompt = console.input("Você > ").strip()
        if prompt.lower() in ("sair", "exit", "quit"):
            isAIinitialized = False  # volta pro menu
            ai = None
            continue

        if not prompt:
            continue

        if prompt.startswith("/"):
            prompt = parse_command(prompt, ai)
        if prompt is None:
            continue

        with console.status("[bold yellow]Duck AI está pensando...[/bold yellow]", spinner="line"):
            resp = ai.ask(prompt, system=SYSTEM_PROMPT)

        console.print(Markdown(resp))
if __name__=="__main__":
    main()