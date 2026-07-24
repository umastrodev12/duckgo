from rich.console import Console
import subprocess
import os

console = Console()

# Schemas

# Write tool Schema
WRITE_TOOL = {
    "type": "function",
    "function": {
        "name": "write_file",
        "description": "Cria ou sobescreve um arquivo desejado.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Caminho do arquivo a ser criado, relativo ao diretório atual."
                },
                "content": {
                    "type": "string",
                    "description": "Conteúdo completo a ser escrito no arquivo."
                }
            },
            "required": ["path", "content"]
        }
    }
}

RUN_COMMAND_TOOL = {
    "type": "function",
    "function": {
        "name": "run_command",
        "description": "Executa um comando no terminal do sistema operacional do usuário.",
        "parameters": {
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "O comando de shell a executar."},
                "reason": {"type": "string", "description": "Motivo de executar esse comando."}
            },
            "required": ["command", "reason"]
        }
    }
}

DANGEROUS_PATTERNS = ["rm -rf", "del /f", "format", "shutdown", "mkfs", ":(){:|:&};:"]

_active_status = None

# Status
def set_active_status(status):
    global _active_status
    _active_status = status


AUTO_APPROVE_WRITE = True   # arquivos: sem confirmação
AUTO_APPROVE_COMMANDS = False  # comandos de shell: continua pedindo

def write_file(path: str, content: str) -> str:
    if not AUTO_APPROVE_WRITE:
        console.print(f"[yellow]Duck AI quer criar:[/yellow] {path}")
        confirm = console.input("[bold]Permitir? (s/n): [/bold]").strip().lower()
        if confirm != "s":
            return "Usuário negou a criação do arquivo."

    console.print(f"[dim]📝 Criando {path}...[/dim]")
    try:
        dirname = os.path.dirname(path)
        if dirname:
            os.makedirs(dirname, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Arquivo '{path}' criado com sucesso."
    except Exception as e:
        return f"Erro ao criar '{path}': {e}"


"""Função que roda um comando shell"""
def run_command(command: str, reason: str) -> str:
    if any(p in command.lower() for p in DANGEROUS_PATTERNS):
        return "Comando bloqueado por segurança."

    console.print(f"[yellow]Duck AI quer executar:[/yellow] [bold cyan]{command}[/bold cyan]")
    console.print(f"[dim]Motivo: {reason}[/dim]")
    confirm = console.input("[bold]Permitir? (s/n): [/bold]").strip().lower()

    if confirm != "s":
        return "Usuário negou a execução do comando."

    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        output = (result.stdout + result.stderr)[:2000]
        return f"Código de saída: {result.returncode}\n{output}"
    except subprocess.TimeoutExpired:
        return "Comando excedeu o tempo limite de 30s."
    except Exception as e:
        return f"Erro: {e}"