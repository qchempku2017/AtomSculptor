import os
from pathlib import Path
from typing import Any, Dict

import yaml


def _load_project_dotenv(dotenv_path: Path) -> None:
    if not dotenv_path.exists() or not dotenv_path.is_file():
        return

    for raw_line in dotenv_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        if line.startswith("export "):
            line = line[len("export ") :].strip()

        if "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()

        if not key:
            continue

        if (value.startswith('"') and value.endswith('"')) or (
            value.startswith("'") and value.endswith("'")
        ):
            value = value[1:-1]

        os.environ.setdefault(key, value)


class Settings:
    """Loads configuration values from a YAML file and/or environment variables.

    Values defined in the environment take precedence over those in the file.
    This keeps secrets out of version control while still allowing a simple
    YAML-based configuration for defaults.
    """

    def __init__(self, config_path: str | Path | None = None) -> None:
        _load_project_dotenv(Path(__file__).resolve().parent / ".env")

        # allow the path to be overridden by environment (useful for tests)
        if config_path is None:
            config_path = os.environ.get("CONFIG_PATH", "config.yaml")
        self._config_path = Path(config_path)
        self._data: Dict[str, Any] = {}

        if self._config_path.exists():
            with open(self._config_path, "r", encoding="utf-8") as f:
                # safe_load will return None for an empty file
                loaded = yaml.safe_load(f)
                if isinstance(loaded, dict):
                    self._data = loaded

        # set defaults and pull from environment if available
        self.PLANNER_MODEL = os.environ.get(
            "PLANNER_MODEL", self._data.get("PLANNER_MODEL", "openai/qwen3-max")
        )
        self.STRUCTURE_BUILDER_MODEL = os.environ.get(
            "STRUCTURE_BUILDER_MODEL", self._data.get("STRUCTURE_BUILDER_MODEL", "openai/qwen3-max")
        )
        self.MP_SEARCHER_MODEL = os.environ.get(
            "MP_SEARCHER_MODEL", self._data.get("MP_SEARCHER_MODEL", "openai/qwen3-max")
        )
        self.SANDBOX_DIR = os.environ.get(
            "SANDBOX_DIR", self._data.get("SANDBOX_DIR", "sandbox/runtime")
        )

    def get_sandbox_client_kwargs(self) -> Dict[str, Any]:
        return {"root_dir": self.SANDBOX_DIR}


# a single, project-wide settings object that can be imported anywhere
settings = Settings()
