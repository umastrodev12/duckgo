import os
import re
from dotenv import load_dotenv
from groq import Groq
from rich.console import Console
from rich.markdown import Markdown

load_dotenv(".env")

class AIClient:
    def __init__(self, api_key: str | None = None, model: str = "qwen/qwen3-32b"):
        self.client = Groq(api_key=api_key or os.environ.get("GROQ_API_KEY"))
        self.model = model
        self.history: list[dict] = []
        self.console = Console()

    def ask(self, prompt: str, system: str | None = None) -> str:
        if system and not self.history:
            self.history.append({"role": "system", "content": system})

        self.history.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.history,
        )

        raw_reply = response.choices[0].message.content
        reply = self._strip_thinking(raw_reply)

        self.history.append({"role": "assistant", "content": raw_reply})
        return reply

    @staticmethod
    def _strip_thinking(text: str) -> str:
        return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()