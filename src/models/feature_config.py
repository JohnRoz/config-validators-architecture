from pydantic import BaseModel

from .. import config_loader


@config_loader.register_config_model(filename="FeatureConfig.json")
class FeatureConfig(BaseModel):
    name: str
    subfeature_names: list[str]
    ...
