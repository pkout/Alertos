from pathlib import Path

import yaml

from core.utils import DotDict, ExtendedEnum

class InvalidEnvironentError(Exception):
    """Raised if the environment is invalid."""

class Environment(ExtendedEnum):
    DEV = 'dev'
    PRD = 'prd'

class Config:
    """Provides access to the config-<env>.yml files."""

    config_file_path_pattern = Path(__file__).parent / '..' / '..' / 'config-{0}.yml'

    def __init__(self, env):
        if env not in Environment.list():
            msg = f'Invalid environment: {env}'
            raise InvalidEnvironentError(msg)

        self._load(str(Config.config_file_path_pattern).format(env))

    def _load(self, config_file_path):
        with open(config_file_path, encoding='utf-8') as f:
            self._conf = yaml.load(f, Loader=yaml.Loader)

    def to_dotdict(self):
        """Returns the config file as a dictionary."""
        return DotDict(self._conf)

    def to_dict(self):
        """Returns the config file as a dictionary."""
        return self._conf

    def __getitem__(self, key):
        return self._conf[key]