from rich.console import Console
import os

console = Console()

def cmd_read(args: list[str]) -> str | None:
    if not args:
        console.print("[red]Uso: /read <arquivo>[/red]")
        return None

    filepath = args[0]
    if not os.path.isfile(filepath):
        console.print(f"[red]Arquivo não encontrado: {filepath}[/red]")
        return None

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        ext = os.path.splitext(filepath)[1].lstrip(".")
        console.print(f"[dim]Lendo {filepath}...[/dim]")
        return f"Arquivo: {filepath}\n```{ext}\n{content}\n```\n\nAnalise esse código."
    except Exception as e:
        console.print(f"[red]Erro ao ler {filepath}: {e}[/red]")
        return None


def cmd_help(args: list[str]) -> None:
    console.print("[bold]Comandos disponíveis:[/bold]")
    console.print("  /read <arquivo>  - analisa um arquivo do projeto")
    console.print("  /clear           - limpa o histórico de conversa")
    console.print("  /help            - mostra essa ajuda")
    return None


def cmd_clear(args: list[str], ai) -> None:
    ai.history.clear()
    console.print("[dim]Histórico limpo.[/dim]")
    return None