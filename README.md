# Configuration Validation Architecture

This repository provides a robust system for defining, loading, and validating configuration files using [Pydantic](https://docs.pydantic.dev/) models and custom validation rules. By splitting out **loading**, **single-file** (Pydantic) validations, and **cross-file** validations, we achieve a scalable, maintainable, and easily extensible architecture.

---

## Table of Contents
1. [Overview of the Architecture](#overview-of-the-architecture)
2. [Benefits](#benefits)
3. [Folder Structure](#folder-structure)
4. [How to Use](#how-to-use)
5. [Adding New Configs](#adding-new-configs)
   - [5.1 Create a New Pydantic Model](#51-create-a-new-pydantic-model)
   - [5.2 Add Single-File Validation](#52-add-single-file-validation)
   - [5.3 Register a Cross-File Validation](#53-register-a-cross-file-validation)

---

## Overview of the Architecture

1. **`BaseConfig` (Single-File Validation Layer):**  
   Each configuration file is defined as a subclass of `BaseConfig`, a thin wrapper around Pydantic’s `BaseModel`. This layer is actually optional, but can be beneficial to provide more control. It is used in various type hints to represent a pydantic model that is also a config.

2. **`ConfigLoader` (I/O and Registration):**  
   - Uses a registry-based approach (`@register_config_model`) to map a JSON filename to a corresponding Pydantic model.  
   - Iterates over `.json` files in a specified directory, parses them, and instantiates each registered model.  
   - Catches Pydantic `ValidationError` and converts them into custom single-file validation exceptions when necessary.

3. **Cross-File Validation (Multi-Model Checks):**  
   - Implemented as independent functions, each describing a particular rule that might involve multiple config models.  
   - Decorated with `@register_validation`.  
   - Automatically discovered and run by `run_validations(...)`, passing the relevant config objects as function arguments.

4. **Custom Exceptions** (in `exceptions.py`):  
   - `BaseValidationError` as a parent for all validation-related issues.  
   - `BaseSingleConfigValidationError` for single-file issues.  
   - `BaseCrossConfigValidationError` for cross-file issues.  
   - Additional specialized exceptions like `ConfigCreationFailedError` for loader errors.

---

## Benefits

- **Clear Separation of Concerns**  
  - **Model definitions** focus on describing data structures (fields, types, and single-file constraints via Pydantic).  
  - **Loading** is centralized in `ConfigLoader`, which references a registry of models and gracefully handles errors.  
  - **Cross-file validations** are modular functions, each dealing with a specific multi-model rule.

- **Ease of Extension**  
  - **Add a new config** by creating a Pydantic model and decorating it with `@register_config_model`.  
  - **Add a new cross-file validation** by writing a small function, decorating with `@register_validation`, and importing it.  

- **Maintainable and Testable**  
  - Single-file validation is testable in isolation (e.g., by instantiating Pydantic models directly).  
  - Cross-file validations are also testable in isolation (pass mock or real config objects to each validator function).  
  - No “god classes” or “mega loader” methods.

- **Robust Error Handling**  
  - All validation errors are custom classes (`BaseValidationError`, etc.), making them easily identifiable and processable.  
  - The loader can either raise on errors or accumulate them, depending on your use case.

---

## Folder Structure

```
my_project/
├─ src/
│  ├─ config_loader.py           # The core loader, with a registry-based approach
│  ├─ exceptions.py              # Custom exception classes for validation
│  ├─ validators/
│  │  ├─ validations_runner.py   # Register/call cross-file validators
│  │  ├─ feature_subfeature_validator.py
│  │  └─ ...                     # Other cross-file validators
│  └─ models/
│     ├─ base_config.py          # Base Pydantic model
│     ├─ feature_config.py
│     ├─ subfeature_config.py
│     └─ ...                     # Additional config models
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

- **`config_loader.py`** uses a decorator `@register_config_model` to map JSON filenames to model classes, then loads them into memory, catching and converting Pydantic errors.  
- **`exceptions.py`** provides our custom exceptions (`BaseValidationError`, etc.).  
- **`base_config.py`** provides `BaseConfig` (a `pydantic.BaseModel` subclass).  
- **`validations_runner.py`** collects cross-file validations (using `@register_validation`) and runs them with `run_validations()`.  
- **`feature_subfeature_validator.py`** is an example cross-file rule that checks references from `FeatureConfig` to `SubFeatureConfig`.  

---

## How to Use

1. **Instantiate `ConfigLoader`** with a directory path (e.g. `tests/test_resources/valid_configs/`).  
2. **Call** `load_configs(should_raise_on_error=True/False)`:
   - Returns a `ConfigLoadResult` object containing:
     - A dictionary of `{model_class: model_instance}` for each successfully loaded config.  
     - A list of single-file validation errors (if any).  
   - If `should_raise_on_error=True`, it raises a `BaseValidationError` immediately if there are any single-file errors.  

3. **Pass the loaded configs** to `run_validations(configs_dict)`:
   - Runs every cross-file validation function that has been registered.  
   - Returns a list of cross-file `BaseValidationError` objects (if any).

Example minimal usage in `main.py`:

```python
from pathlib import Path
from src.config_loader import ConfigLoader
from src.validators.validations_runner import run_validations

def main():
    loader = ConfigLoader(Path("./tests/test_resources/valid_configs"))
    load_result = loader.load_configs(should_raise_on_error=False)
    configs, single_file_errors = load_result.unpack()

    # Print single-file errors
    for err in single_file_errors:
        print("Single-file validation error:", err)

    # Cross-file checks
    cross_file_errors = run_validations(configs)
    for err in cross_file_errors:
        print("Cross-file validation error:", err)

    print("Done!")

if __name__ == "__main__":
    main()
```

---

## Adding New Configs

### 5.1. Create a New Pydantic Model

1. **Define** a new subclass of `BaseConfig` in `src/models/`.  
2. **Decorate** it with `@register_config_model(filename="SomeNewConfig.json")` so that the loader knows which JSON file it corresponds to.

**Example**:
```python
# src/models/some_new_config.py

from pydantic import Field
from ..models.base_config import BaseConfig
from ..config_loader import register_config_model

@register_config_model(filename="SomeNewConfig.json")
class SomeNewConfig(BaseConfig):
    # Define fields
    required_field: int = Field(..., ge=1, description="Must be >= 1")
    optional_field: str | None = None
```

Place a **`SomeNewConfig.json`** file in your configs folder (e.g., `tests/test_resources/valid_configs/`), matching whatever structure you need:
```json
{
  "required_field": 42,
  "optional_field": "example text"
}
```

### 5.2. Add Single-File Validation

Pydantic allows you to define single-file constraints in multiple ways:

- **Field constraints** (like `ge=1` above).  
- **`@validator` or `@root_validator`** to implement custom logic.

If a JSON input violates these constraints, a `pydantic.ValidationError` is raised and then translated to a `BaseSingleConfigValidationError` inside the loader.

Example `@validator`:

```python
from pydantic import validator

@register_config_model(filename="SomeNewConfig.json")
class SomeNewConfig(BaseConfig):
    required_field: int
    optional_field: str | None = None

    @validator("required_field")
    def check_required_field(cls, val):
        if val > 100:
            raise ValueError("required_field must not exceed 100")
        return val
```

### 5.3. Register a Cross-File Validation

If you need to enforce a rule involving **multiple** config models, write a **function** with typed parameters:

1. **Annotate** the parameters with the model classes you need.  
2. **Decorate** the function with `@register_validation`.  
3. **Return** an iterable of `BaseValidationError` objects (or none if no issues).

**Example** (`src/validators/some_new_cross_validator.py`):

```python
from typing import Iterable
from ..exceptions import BaseCrossConfigValidationError, BaseValidationError
from ..models.some_new_config import SomeNewConfig
from ..models.feature_config import FeatureConfig
from .validations_runner import register_validation

@register_validation
def ensure_feature_and_newconfig_are_consistent(
    new_cfg: SomeNewConfig,
    feature_cfg: FeatureConfig
) -> Iterable[BaseValidationError]:
    errors = []
    # Example cross-check
    if new_cfg.required_field < 50 and any(f.name == "SpecialFeature" for f in feature_cfg.features):
        errors.append(BaseCrossConfigValidationError(
            "SpecialFeature requires required_field >= 50"
        ))
    return errors
```

**Important**: Make sure the module is imported (either in `validators/__init__.py` or directly in your code) so that the decorator actually runs. Once imported, the validation is automatically executed in `run_validations()` if both `SomeNewConfig` and `FeatureConfig` are loaded.

---

### Final Notes

- **Single-file validations** remain where they belong—in each Pydantic model class.  
- **Cross-file validations** are decoupled, living in small modules or functions.  
- The **loader** is the only place that deals with I/O and error translation, keeping your code maintainable.

Enjoy creating new configs and validations in this **clean, scalable architecture**! 