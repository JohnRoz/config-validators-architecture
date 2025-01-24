from .. import config_loader
from .base_config import BaseConfig


class SingleSubFeatureConfig(BaseConfig):
    name: str
    ...


@config_loader.register_config_model(filename="SubFeatureConfig.json")
class SubFeatureConfig(BaseConfig):
    subfeatures: list[SingleSubFeatureConfig]
