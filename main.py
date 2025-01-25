from src.config_loader import ConfigLoader
from src.cross_config_validations import cross_config_validations_runner
from src.exceptions import BaseValidationError

# Example main:


def main_without_raising():
    configs_dir = "./tests/test_resources/cross_configs/invalid_configs"
    loader = ConfigLoader.load(configs_dir)

    for err in loader.config_creation_errors:
        print(err)

    cross_config_validation_errors = cross_config_validations_runner.run_validations(loader.configs)
    all_validation_errors = loader.single_config_validation_errors + cross_config_validation_errors

    for err in all_validation_errors:
        print(err)
    else:
        print("All validations passed!")


def main_with_raising():
    configs_dir = "./tests/test_resources/cross_configs/invalid_configs"
    try:
        loader = ConfigLoader.load(configs_dir, should_raise_on_error=True)
        cross_config_validations_runner.run_validations(loader.configs, should_raise_on_error=True)
    except* BaseValidationError as e:
        for validation_err in e.exceptions:
            print("Caught a validation error:\n", validation_err)
    except* BaseException as ex_group:
        for err in ex_group.exceptions:
            print(err)
    else:
        print("All validations passed!")


if __name__ == "__main__":
    main_with_raising()
