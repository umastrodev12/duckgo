from rich.console import Console
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

def write_file(path: str, content: str):
    console.print(f"[yellow]Duck AI quer criar/sobrescrever: {path}[/yellow]")
    console.print(f"[dim]{content[:200]}{'...' if len(content) > 200 else ''}[/dim]")
    confirm = console.input("[bold]Permitir? (s/n): [/bold]").strip().lower()

    if confirm != "s":
        return "Usuário negou a escrita do arquivo."

    try:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Arquivo '{path}' criado com sucesso."
    except Exception as e:
        return f"Erro ao criar '{path}': {e}"