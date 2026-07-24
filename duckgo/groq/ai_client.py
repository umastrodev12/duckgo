import os
import re
from dotenv import load_dotenv
from groq import Groq
from rich.console import Console
from rich.markdown import Markdown
from duckgo.tools import WRITE_TOOL, RUN_COMMAND_TOOL, run_command, write_file
import json

load_dotenv(".env")

TOOLS = [WRITE_TOOL, RUN_COMMAND_TOOL]
TOOL_FUNCTIONS = {
    "write_file": write_file,
    "run_command": run_command,
    }

class AIClient:
    def __init__(self, api_key: str, model: str = "qwen/qwen3-32b"):
        self.client = Groq(api_key=api_key)
        self.model = model
        self.history: list[dict] = []
        
    def ask(self, prompt: str, system: str | None = None) -> str:
        if system and not self.history:
            self.history.append({"role": "system", "content": system})

        self.history.append({"role": "user", "content": prompt})

        max_iterations = 15
        for _ in range(max_iterations):
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.history,
                tools=TOOLS,
                tool_choice="auto",
            )

            message = response.choices[0].message

            if not message.tool_calls:
                reply = message.content
                self.history.append({"role": "assistant", "content": reply})
                return reply

            self.history.append(message)

            for call in message.tool_calls:
                args = json.loads(call.function.arguments)
                func = TOOL_FUNCTIONS[call.function.name]
                result = func(**args)

                self.history.append({
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": result,
                })

        return "Limite de iterações atingido — a tarefa pode ser complexa demais para uma única resposta."
    @staticmethod
    def _strip_thinking(text: str) -> str:
        return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()
