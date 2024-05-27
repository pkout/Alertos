from pathlib import Path

import yaml

from core.utils import DotDict


CONFIG_FILE_PATH = Path(__file__) / '..' / '..' / 'config.yml'

class ConfigFileNotFoundError(Exception):
    """Raised if the config file is not found."""

class Config:

    def __init__(self, config_file_path=CONFIG_FILE_PATH):
        self._load(config_file_path)

    def _load(self, config_file_path):
        if not Path(config_file_path).exists():
            msg = f'Config file path ${config_file_path} not found!'
            raise ConfigFileNotFoundError(msg)

        with open(config_file_path, encoding='utf-8') as f:
            self._conf = DotDict(yaml.load(f, Loader=yaml.Loader))

    def to_dict(self):
        """Returns the config file as a dictionary."""
        return self._conf