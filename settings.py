import os
from pathlib import Path
from typing import Any, Dict

import yaml


class Settings:
    """Loads configuration values from a YAML file and/or environment variables.

    Values defined in the environment take precedence over those in the file.
    This keeps secrets out of version control while still allowing a simple
    YAML-based configuration for defaults.
    """

    def __init__(self, config_path: str | Path | None = None) -> None:
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


# a single, project-wide settings object that can be imported anywhere
settings = Settings()
