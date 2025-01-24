from pydantic import BaseModel

from .. import config_loader


@config_loader.register_config_model(filename="DatabaseConfig.json")
class DatabaseConfig(BaseModel):
    host: str
    port: str
    ...
