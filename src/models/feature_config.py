from typing import Self

import pydantic

from .. import config_loader
from .base_config import BaseConfig


class SingleFeatureConfig(BaseConfig):
    name: str
    subfeature_names: list[str] = pydantic.Field(..., description="List of subfeature names, cannot be empty.")
    ...

    @pydantic.field_validator("subfeature_names", mode="after")
    @classmethod
    def validate_subfeature_names(cls, subfeature_names: list[str]) -> list[str]:
        if not subfeature_names:
            raise ValueError("subfeature_names cannot be empty.")

        return subfeature_names


@config_loader.register_config_model(filename="FeatureConfig.json")
class FeatureConfig(BaseConfig):
    features: list[SingleFeatureConfig] = pydantic.Field(..., description="List of feature configs, cannot be empty.")

    # Root validation to ensure no subfeature_names is empty in any SingleFeatureConfig
    @pydantic.model_validator(mode="after")
    def validate_subfeature_names_in_features(self) -> Self:
        if not self.features:
            raise ValueError("Features list cannot be empty")

        for feature in self.features:
            if not feature.subfeature_names:
                raise ValueError(f"Feature '{feature.name}' has an empty subfeature_names list.")

        return self
