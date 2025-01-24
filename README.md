# Config Validation Architecture

This project demonstrates a **modular** approach for loading JSON configuration files and validating them.  
We separate the concerns of:

1. **Loading config files** into Pydantic-based data models (and performing single-file validations).  
2. **Cross-file validations** for constraints that span multiple config types.

---

## 1. Architecture & Benefits

### 1.1. Layers of Responsibility

1. **Model Layer (Pydantic)**  
   - Each config file corresponds to a Pydantic model that extends a shared `BaseConfig`.  
   - This layer is responsible for describing field structures and single-file validations (e.g., using `@root_validator` or `@validator`).  

2. **Config Loader**  
   - Scans a directory for JSON files.  
   - Matches each file by filename to a Pydantic model (via `@register_config_model`).  
   - Instantiates the models. If a Pydantic `ValidationError` arises, it can be caught and translated into custom error types (`BaseValidationError`).

3. **Cross-File Validation (Validators)**  
   - Complex constraints that involve **multiple config models** are implemented as small, independent validation functions.  
   - Each validation function is decorated with `@register_validation`, which auto-registers it.  
   - A runner (`run_validations`) automatically calls all registered validations, passing in the relevant config objects.

### 1.2. Benefits

- **Modularity**:  
  - Each config file has its own dedicated Pydantic model.  
  - Cross-file checks are isolated into small functions, avoiding one huge “god” validator class.  

- **Ease of Extension**:  
  - Adding a new config requires creating a JSON file and a corresponding Pydantic model with `@register_config_model`.  
  - Cross-file validations are added by simply writing a new function with `@register_validation`.  
  - No need to modify a monolithic loader or a single “mega-validation” method.

- **Clarity & Maintainability**:  
  - Single-file data constraints stay where they belong—in each model.  
  - Multi-file relationships are handled by small, focused validation functions.  
  - No large classes or complicated condition checks spread across the codebase.

- **Testability**:  
  - You can test each model independently for single-file validation.  
  - You can test each cross-file validator function in isolation.  

---

## 2. Directory Structure

An example layout:

```
my_project/
├─ src/
│  ├─ config_loader.py
│  ├─ exceptions.py
│  ├─ validators/
│  │  ├─ validations_runner.py
│  │  ├─ feature_subfeature_validator.py
│  │  └─ ...
│  └─ models/
│     base_config.py
│     ├─ feature_config.py
│     ├─ subfeature_config.py
│     └─ ...
├─ tests/
│  └─ test_resources/
│     ├─ valid_configs/
│     │  ├─ FeatureConfig.json
│     │  └─ SubFeatureConfig.json
│     └─ invalid_configs/
│        ├─ FeatureConfig.json
│        └─ SubFeatureConfig.json
└─ main.py
```

1. **`src/models/`**: Holds all Pydantic models.  
2. **`src/config_loader.py`**: Implements `ConfigLoader`, which loads JSON files and instantiates Pydantic models.  
3. **`src/validators/`**: Contains multiple modules of cross-file validation logic, plus a `validations_runner.py` that orchestrates the registered validations.  
4. **`tests/test_resources/valid_configs/`**: Example JSON files.  
5. **`main.py`**: Entry point to load configs and run validations.

---

## 3. Usage

### 3.1. Running the Program

1. **Place** your `.json` config files in the designated directory (e.g., `tests/test_resources/valid_configs/`).  
2. **Run** the `main.py` script, which in turn:  
   - Instantiates a `ConfigLoader` pointing to `tests/test_resources/valid_configs/`.  
   - Loads each JSON into the respective Pydantic model.  
   - Invokes `run_validations()` to perform cross-file checks.

A sample `main.py` might look like this:

```python
from pathlib import Path

from src.config_loader import ConfigLoader
from src.validators import validations_runner

def main():
    # Point to the directory containing JSON files
    loader = ConfigLoader(Path("./tests/test_resources/valid_configs"))
    available_configs = loader.load_configs()

    # Run cross-file validations
    errors = validations_runner.run_validations(available_configs)

    if errors:
        for err in errors:
            print(f"Validation Error: {err}")
    else:
        print("All cross-file validations passed!")

if __name__ == "__main__":
    main()
```

---

## 4. Adding a New Config Model

Below is a **detailed** example of adding a new config file—**`AwesomeFeatureConfig.json`**—and hooking it into both single-file and cross-file validations.

### 4.1. Create the JSON File

Create a file named **`AwesomeFeatureConfig.json`** in `tests/test_resources/valid_configs/`, with contents like:

```json
{
  "enabled": true,
  "threshold": 150
}
```

### 4.2. Define the New Pydantic Model

In `src/models/awesome_feature_config.py` (or a similar filename):

```python
from pydantic import root_validator
from ..config_loader import register_config_model
from .base_config import BaseConfig
from ..validators.validation_exceptions import BaseValidationError

@register_config_model(filename="AwesomeFeatureConfig.json")
class AwesomeFeatureConfig(BaseConfig):
    enabled: bool
    threshold: int

    @root_validator
    def check_threshold(cls, values):
        threshold = values.get("threshold")
        if threshold > 1000:
            # This raises a Pydantic ValidationError internally
            raise ValueError("Threshold must not exceed 1000")
        return values
```

**Key Points**:
- `@register_config_model(filename="AwesomeFeatureConfig.json")` ties the model to that JSON file.  
- Any single-file constraints you need can be placed here (or using `@validator` decorators).

### 4.3. Handling Pydantic Validation Errors

If `threshold` is too large or the JSON is malformed, Pydantic will raise a `ValidationError`.  
To convert that to our custom `BaseValidationError`, we do something like this in `config_loader.py`:

```python
import json
from pathlib import Path
from pydantic import ValidationError
from typing import Callable, TypeVar

from src.models.base_config import BaseConfig
from src.validators.validation_exceptions import BaseValidationError

_MODEL_REGISTRY: dict[str, type[BaseConfig]] = {}
_T_CONFIG_TYPE = TypeVar("_T_CONFIG_TYPE", bound=type[BaseConfig])

def register_config_model(*, filename: str) -> Callable[[_T_CONFIG_TYPE], _T_CONFIG_TYPE]:
    def decorator(cls: _T_CONFIG_TYPE) -> _T_CONFIG_TYPE:
        _MODEL_REGISTRY[filename] = cls
        return cls
    return decorator

class ConfigLoader:
    def __init__(self, configs_dir: Path) -> None:
        self.configs_dir = configs_dir

    def load_configs(self) -> dict[type[BaseConfig], BaseConfig]:
        configs = {}
        for file in self.configs_dir.glob("*.json"):
            if file.name not in _MODEL_REGISTRY:
                continue

            config_cls = _MODEL_REGISTRY[file.name]
            try:
                data = json.loads(file.read_text())
                configs[config_cls] = config_cls(**data)
            except ValidationError as e:
                print(f"Error loading '{file.name}':")
                for err in e.errors():
                    # Convert pydantic's error to your BaseValidationError
                    msg = err.get("msg", "Unknown error")
                    loc = err.get("loc", [])
                    print(BaseValidationError(f"Pydantic validation failed: {msg}", location=loc))

        return configs
```

### 4.4. Adding a Cross-File Validator

Let’s say we want a rule: **If** `AwesomeFeatureConfig` is enabled **AND** `FeatureConfig` includes a feature named `"SomeFeature"`, then `threshold` must be at least `100`.

1. Create a file: `src/validators/awesome_feature_validator.py`:

   ```python
   from typing import Iterable
   from .validations_runner import register_validation
   from ..models.feature_config import FeatureConfig
   from ..models.awesome_feature_config import AwesomeFeatureConfig
   from .validation_exceptions import BaseValidationError

   @register_validation
   def validate_awesome_feature_threshold(
       awesome_cfg: AwesomeFeatureConfig,
       feature_cfg: FeatureConfig
   ) -> Iterable[BaseValidationError]:
       errors = []
       if awesome_cfg.enabled:
           has_some_feature = any(f.name == "SomeFeature" for f in feature_cfg.features)
           if has_some_feature and awesome_cfg.threshold < 100:
               errors.append(BaseValidationError(
                   "Threshold must be >= 100 when SomeFeature is present!",
                   threshold=awesome_cfg.threshold
               ))
       return errors
   ```

2. **Import** that validator so the decorator runs. In `src/validators/__init__.py`:

   ```python
   from . import feature_subfeature_validator
   from . import awesome_feature_validator  # Ensure it's imported
   ```

3. Now, when `run_validations()` is called, it will automatically pick up `validate_awesome_feature_threshold()` **if** both `AwesomeFeatureConfig` and `FeatureConfig` are loaded.

---

## 5. Example Files & Testing

### 5.1. Example Directory and Files

Under `tests/test_resources/valid_configs/`, you might have:

- **`FeatureConfig.json`**:
  ```json
  {
    "features": [
      {
        "name": "SomeFeature",
        "subfeature_names": ["sub_1", "sub_2"]
      }
    ]
  }
  ```
- **`AwesomeFeatureConfig.json`**:
  ```json
  {
    "enabled": true,
    "threshold": 50
  }
  ```
- **`SubFeatureConfig.json`**:
  ```json
  {
    "subfeatures": [
      { "name": "sub_1" },
      { "name": "sub_2" }
    ]
  }
  ```

When you run your `main.py`, the loader will instantiate all three configs, then **`validate_awesome_feature_threshold`** will see:

- `awesome_cfg.enabled == true`  
- `FeatureConfig` has `"SomeFeature"`  
- `awesome_cfg.threshold` is `50` -> This triggers a cross-file validation **error** because it’s less than `100`.

You’ll see a `BaseValidationError` printed with `"Threshold must be >= 100 when SomeFeature is present!"`.

---

## 6. Summary

1. **Single-file validations**: Use Pydantic’s validators to constrain data in each `BaseConfig` subclass (e.g., `FeatureConfig`, `AwesomeFeatureConfig`). You can catch and translate `ValidationError` into `BaseValidationError`.  
2. **Cross-file validations**: Define small, typed functions with the `@register_validation` decorator. They are automatically discovered and run by `run_validations()`.  
3. **Easy to Extend**: 
   - To add **new config**: create a new `.json` file + new Pydantic model + `@register_config_model`.  
   - To add **new cross-file checks**: write a new function with `@register_validation`.  

This approach keeps your code **modular**, **maintainable**, and **testable**, avoiding monolithic loaders or validators. Enjoy a clear separation of responsibilities, allowing each component (loader, single-file validation, cross-file validation) to evolve independently.