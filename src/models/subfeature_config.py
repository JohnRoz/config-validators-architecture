from pydantic import BaseModel

from .. import config_loader


class SingleSubFeatureConfig(BaseModel):
    name: str
    ...


@config_loader.register_config_model(filename="SubFeatureConfig.json")
class SubFeatureConfig(BaseModel):
    subfeatures: list[SingleSubFeatureConfig]
