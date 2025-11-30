# Unit tests

Set of unit tests for Retromancer. 
The aim is to test addon addon registration and unregistration, operators, custom nodes and properties, all designed to run across multiple Blender versions.
Tests are written using Python's built-in `unittest` framework.

## Usage

The test shell scripts handle:

1. Downloading all required Blender versions into the `tests/` directory  
2. Setting up a symbolic link for the `retromancer` addon in `$HOME/.config/blender/<version>/scripts/addons`  
3. Running `unit_tests.py` using the Blender executable:

    ./blender --background --factory-startup --python  ../unit_tests.py

### Minimal test (major versions only)

Runs a minimal set of tests on major Blender versions specified in `releases.txt`:

    retromancer/tests/test_minimal.sh

### Full test (all versions)

Runs a full set of tests on all Blender versions specified in `releases.txt`:

    retromancer/tests/test_full.sh

## `releases.txt` file syntax

`releases.txt` lists Blender releases in the following format:

```
<major version>:<minor version range start>-<minor version range end>
```

Example:

```
4.2:0-16
4.3:0-2
4.4:0-3
4.5:0-5
```