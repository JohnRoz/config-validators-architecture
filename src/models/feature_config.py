from .. import config_loader
from .base_config import BaseConfig


class SingleFeatureConfig(BaseConfig):
    name: str
    subfeature_names: list[str]
    ...


@config_loader.register_config_model(filename="FeatureConfig.json")
class FeatureConfig(BaseConfig):
    features: list[SingleFeatureConfig]
