from .. import config_loader
from .base_config import BaseConfig


@config_loader.register_config_model(filename="MyNewThingConfig.json")
class MyNewThingConfig(BaseConfig):
    name: str
    statuses: list[str]
    ...
