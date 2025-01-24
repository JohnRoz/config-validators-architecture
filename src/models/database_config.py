from .. import config_loader
from .base_config import BaseConfig


@config_loader.register_config_model(filename="DatabaseConfig.json")
class DatabaseConfig(BaseConfig):
    host: str
    port: str
    ...
