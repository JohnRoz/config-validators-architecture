from pydantic import BaseModel

from .. import config_loader


@config_loader.register_config_model(filename="MyNewThingConfig.json")
class MyNewThingConfig(BaseModel):
    name: str
    statuses: list[str]
    ...
