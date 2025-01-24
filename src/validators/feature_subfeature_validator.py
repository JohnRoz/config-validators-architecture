from typing import Iterable

from ..models.feature_config import FeatureConfig
from ..models.subfeature_config import SubFeatureConfig
from . import validations_runner
from .validation_exceptions import BaseValidationError


@validations_runner.register_validation
def validate_feature_not_reference_non_existant_subfeature(
    feature_config: FeatureConfig, subfeature_config: SubFeatureConfig
) -> Iterable[BaseValidationError]:
    validation_errors = []

    all_subfeature_names = {subfeature.name for subfeature in subfeature_config.subfeatures}
    all_referenced_subfeatures = {name for feature in feature_config.features for name in feature.subfeature_names}

    if undefined_subfeatures := all_referenced_subfeatures - all_subfeature_names:
        for undefined_subfeature in undefined_subfeatures:
            validation_errors.append(
                BaseValidationError(
                    f"Referenced subfeature {undefined_subfeature} is undefined",
                    undefined_subfeature=undefined_subfeature,
                )
            )

    return validation_errors
