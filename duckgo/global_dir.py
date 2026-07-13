import os
import json

GLOBAL_DIR = ".duck"
CONFIG_FILE = "config.json"
DEFAULT_MODEL = "qwen/qwen3-32b"

class globalDir:
    def  __init__(self, root) -> None:
        self.root = os.path.abspath(root)
        self.dir = os.path.join(self.root, GLOBAL_DIR)
        self.config_path = os.path.join(self.dir, CONFIG_FILE)

    @classmethod
    def findGlobalDuck(cls):
        here = os.path.abspath(os.getcwd())
        while True:
            if os.path.isdir(os.path.join(here, GLOBAL_DIR)):
                return cls(here)
            dir = os.path.dirname(here)
            if dir == here:
                return None

            here = dir

    def exists(self):
        return os.path.isdir(self.dir)

    def createGlobalDuck(self):
        os.makedirs(self.dir)

    def load_config(self) -> dict:
        if os.path.exists(self.config_path):
            with open(self.config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"model": DEFAULT_MODEL}

    def save_config(self, config: dict) -> None:
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)

    def get_model(self) -> str:
        return self.load_config().get("model", DEFAULT_MODEL)

    def set_model(self, model: str) -> None:
        config = self.load_config()
        config["model"] = model
        self.save_config(config)