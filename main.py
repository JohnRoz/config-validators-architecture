from src.config_loader import ConfigLoader
from src.cross_config_validations import validations_runner

# Example main:


def main():
    configs_dir = "./tests/test_resources/invalid_configs"
    loader = ConfigLoader.load(configs_dir)

    for err in loader.config_creation_errors:
        print(err)

    cross_config_validation_errors = validations_runner.run_validations(loader.configs)
    all_validation_errors = loader.single_config_validation_errors + cross_config_validation_errors

    for err in all_validation_errors:
        print(err)
    else:
        print("All validations passed!")


if __name__ == "__main__":
    main()
