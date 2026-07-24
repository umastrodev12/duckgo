from duckgo.plugin.duck_plugin import duckPlugin
from duckgo.global_dir import globalDir
from duckgo.groq.ai_client import AIClient
from duckgo.tools import write_file, WRITE_TOOL, RUN_COMMAND_TOOL, run_command, set_active_status
from duckgo.command_reader import (
    cmd_clear,
    cmd_help,
    cmd_read,
)
from rich.markdown import Markdown
from dotenv import load_dotenv
from rich.panel import Panel
from rich.align import Align
from rich.text import Text
from rich.console import Console
from rich.rule import Rule
import datetime
import getpass
import random
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

TOOLS = [WRITE_TOOL, RUN_COMMAND_TOOL]
TOOL_FUNCTIONS = {
    "write_file": write_file,
    "run_command": run_command,
}

SYSTEM_PROMPT = """Você é o Duck AI, um assistente pessoal de programação.
Seja direto e técnico. Você também pode responder dúvidas simples.
Sua língua fluente é Português Brasileiro.

Você roda dentro de um terminal chamado Duck Go, que tem os seguintes comandos disponíveis para o usuário:
- /read <arquivo> - lê e envia o conteúdo de um arquivo do projeto para você analisars
- /clear - limpa o histórico da conversa atual
- /help - mostra a lista de comandos

Você também tem as seguintes ferramentas:
- run_command(command, reason): executa qualquer comando de shell, incluindo git e gh (GitHub CLI)
- write_file(path, content): cria ou sobrescreve um arquivo

Não use muitos títulos: Não use títulos para bagunçar sua resposta, lembre-se, você é como se fosse um "Mini Claude Code", saiba mais sobre ele no link: https://claude.com/product/claude-code
"""

THINKING_WORDS = [
    "Pensando", "Refletindo", "Cozinhando", "Nadando",
    "Investigando", "Ponderando", "Processando", "Quackando",
]

TIPS = [
    'Tente "cria um arquivo config.json com..."',
    'Tente "lê o main.py e me explica o que faz"',
    'Tente "roda os testes do projeto"',
    'Tente "faz um commit dessas mudanças"',
    'Tente "/help" para ver os comandos',
]

def show_prompt_line():
    console.print(Rule(style="dim"))

def show_prompt_hint():
    tip = random.choice(TIPS)
    console.print(f"[dim]{tip}[/dim]")

def get_thinking_word() -> str:
    return random.choice(THINKING_WORDS)

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


def get_greeting() -> str:
    hour = datetime.datetime.now().hour
    if hour < 12:
        return "Bom dia"
    elif hour < 18:
        return "Boa tarde"
    return "Boa noite"


def show_welcome(duck, model: str):
    console.clear()

    usuario = getpass.getuser()
    greeting = get_greeting()
    cwd = os.getcwd()

    body = Text()
    body.append(f"{greeting}, {usuario} 🦆\n\n", style="bold")
    body.append("Diretório: ", style="dim")
    body.append(f"{cwd}\n", style="cyan")
    body.append("Modelo: ", style="dim")
    body.append(f"{model}\n\n", style="yellow")

    body.append("Dicas para começar:\n", style="bold dim")
    body.append("  • Peça para criar, ler ou editar arquivos do projeto\n", style="dim")
    body.append("  • Peça para rodar comandos, testes, ou fazer commits\n", style="dim")
    body.append("  • ", style="dim")
    body.append("/help", style="green")
    body.append(" mostra os comandos disponíveis\n", style="dim")
    body.append("  • ", style="dim")
    body.append("sair", style="red")
    body.append(" encerra a sessão", style="dim")

    panel = Panel(
        body,
        title="[bold yellow]🦆 Duck Go[/bold yellow]",
        border_style="yellow",
        padding=(1, 3),
        expand=False,
    )

    console.print(Align.center(panel))
    console.print()

def main():
    global ai

    duck = globalDir.findGlobalDuck()
    if duck is None:
        duck = globalDir(os.getcwd())
        duck.createGlobalDuck()

    api_key = ensure_api_key(duck)
    ai = AIClient(api_key=api_key, model=duck.get_model())

    duck.load_config()

    show_welcome(duck, model=duck.get_model())

    while True:
        
        show_prompt_line()
        prompt = console.input("Você > ").strip()
        show_prompt_line()
        if prompt.lower() in ("sair", "exit", "quit"):
            console.clear()
            return

        if prompt == "criar duck plugin":
            plugin = duckPlugin(os.getcwd())
            plugin.create_duck_plugin_dir()

        if not prompt:
            continue


        if prompt.startswith("/"):
            prompt = parse_command(prompt, ai)
        if prompt is None:
            continue

        console.print(f"[dim]🦆 {get_thinking_word()}...[/dim]")

        resp = ai.ask(prompt, system=SYSTEM_PROMPT)
        console.print(Markdown(resp))
if __name__=="__main__":
    main()