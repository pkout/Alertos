from core.config import Config, Environment

config = Config(Environment.DEV.value).to_dotdict()