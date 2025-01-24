from pathlib import Path

from src.config_loader import ConfigLoader
from src.validators import validations_runner

# Example main:


def main():
    loader = ConfigLoader(Path("./tests/test_resources/invalid_configs"))
    available_configs, single_config_errors = loader.load_configs().unpack()

    cross_config_errors = validations_runner.run_validations(available_configs)

    if single_config_errors or cross_config_errors:
        for err in single_config_errors + cross_config_errors:
            print(err)
    else:
        print("All cross-file validations passed!")


if __name__ == "__main__":
    main()
