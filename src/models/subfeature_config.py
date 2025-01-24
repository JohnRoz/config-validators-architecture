from pydantic import BaseModel

from .. import config_loader


@config_loader.register_config_model(filename="SubFeatureConfig.json")
class SubFeatureConfig(BaseModel):
    name: str
    ...
