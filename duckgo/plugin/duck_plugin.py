from rich.console import Console
import json
import os

console = Console()

PLUGIN_DIR = ".duck-plugin"

class duckPluginAPI:
    def __init__(self, commands: dict, tools: list, tool_functions: dict) -> None:
        self._commands = commands
        self._tools = tools
        self._tool_funcs = tool_functions

    def add_command(self, name: str, handler):
        self._commands[name] = handler

    def add_tool(self, tool_schema: dict, function):
        self._tools.append(tool_schema)
        self._tool_funcs[tool_schema["function"]["name"]] = function

class duckPlugin:
    def __init__(self, root) -> None:
        self.root = os.path.abspath(root)
        self.dir = os.path.join(self.root, PLUGIN_DIR)

    def create_duck_plugin_dir(self):
        duck_plugin_model = {
        "$schema": "http://127.0.0.1:8000/duckgo-plugin-schema",
        "name": "duckgo-plugins",
        "version": "0.0.1",
        "description": "A Bunch of plugins for DuckGo.",
        "owner": {
            "name": "Astro",
            "email": "ajuda.perfect.tea@zohomail.com"
        }
    }

        dirname = os.path.dirname(os.path.abspath(self.dir))
        json_path = os.path.normpath(os.path.join(
        dirname, "plugins.json"
        ))

        console.print("[yellow] Criando .duck-plugin... [yellow]")
        os.makedirs(self.dir, exist_ok=True)
        with open(json_path, "w", encoding='utf-8') as f:
            json.dump(duck_plugin_model, f, indent=4, ensure_ascii=False)
