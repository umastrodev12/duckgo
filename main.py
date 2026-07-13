from duckgo.global_dir import globalDir
from duckgo.groq.ai_client import AIClient
from duckgo.command_reader import (
    cmd_clear,
    cmd_help,
    cmd_read
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
}

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

            if prompt.lower() == "iniciar chat":
                ai = AIClient(model=duck.get_model())
                isAIinitialized = True

            if prompt.lower() in ("sair", "exit", "quit"):
                break

            if not prompt:
                continue
        

        console.print("[bold green] Iniciando Chat...[/bold green]")
        time.sleep(2)
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

        resp = ai.ask(prompt, system="Você é um assistente pessoal de programação que analisa código enviado pelo usuário. Seja direto e técnico. Você também pode responder dúvidas simples. Sua língua fluente é Português Brasileiro, seu nome é Duck AI.")
        console.print(Markdown(resp))
if __name__=="__main__":
    main()