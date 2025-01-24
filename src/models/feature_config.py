from pydantic import BaseModel

from .. import config_loader


class SingleFeatureConfig(BaseModel):
    name: str
    subfeature_names: list[str]
    ...


@config_loader.register_config_model(filename="FeatureConfig.json")
class FeatureConfig(BaseModel):
    features: list[SingleFeatureConfig]
