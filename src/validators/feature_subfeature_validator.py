from typing import Iterable

from ..exceptions import BaseCrossConfigValidationError, BaseValidationError
from ..models.feature_config import FeatureConfig
from ..models.subfeature_config import SubFeatureConfig
from . import validations_runner


@validations_runner.register_validation
def validate_feature_not_reference_non_existant_subfeature(
    feature_config: FeatureConfig, subfeature_config: SubFeatureConfig
) -> Iterable[BaseValidationError]:
    err_msg = "Referenced subfeature is undefined"
    validation_errors = []

    all_subfeature_names = {subfeature.name for subfeature in subfeature_config.subfeatures}
    all_referenced_subfeatures = {name for feature in feature_config.features for name in feature.subfeature_names}

    if undefined_subfeatures := all_referenced_subfeatures - all_subfeature_names:
        for undefined_subfeature in undefined_subfeatures:
            validation_errors.append(
                BaseCrossConfigValidationError(
                    err_msg,
                    undefined_subfeature=undefined_subfeature,
                )
            )

    return validation_errors
