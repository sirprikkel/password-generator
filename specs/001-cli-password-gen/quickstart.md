# Quickstart: CLI Password Generator

**Feature**: `001-cli-password-gen` | **Date**: 2026-02-18

---

## Prerequisites

- Python 3.8 or higher
- `pip` (bundled with Python)

---

## Install (from source)

```sh
# Clone and enter the project
git clone <repo-url>
cd password-generator

# Install in editable mode (development)
pip install -e .

# Verify the entry point is available
passgen --help
```

---

## Usage

```sh
# Generate a 16-character password (default)
passgen

# Generate a 32-character password
passgen --length 32

# Generate without symbols (letters + numbers only)
passgen --no-symbols

# Generate without numbers (letters + symbols only)
passgen --no-numbers

# Generate letters only
passgen --no-symbols --no-numbers

# Compose: generate and pipe to xclip (Linux, alternative clipboard)
passgen | xclip -selection clipboard
```

---

## Run Tests

```sh
# Install with test dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# Run with coverage report
pytest --cov=passgen --cov-report=term-missing

# Run only unit tests
pytest tests/unit/

# Run only integration tests
pytest tests/integration/
```

---

## Project Layout

```text
passgen/         # source package
├── __init__.py
├── cli.py       # argparse entrypoint
├── generator.py # password generation (secrets module)
└── clipboard.py # pyperclip wrapper

tests/
├── unit/
│   ├── test_generator.py
│   └── test_cli.py
└── integration/
    └── test_passgen.py

pyproject.toml   # package metadata + entry point declaration
```

---

## Expected Behaviour

| Scenario | stdout | stderr | Exit |
|----------|--------|--------|------|
| Default run | generated password | `Password copied to clipboard.` | `0` |
| `--length 4` (invalid) | (empty) | `Error: --length must be at least 8.` | `1` |
| Headless / no display | generated password | `Warning: could not copy to clipboard…` | `2` |

---

## Development Notes

- **TDD is mandatory**: write failing tests before any implementation code (Constitution Principle III).
- Password value MUST go only to `stdout`. Do not print it to `stderr` or any log in tests.
- `secrets` module is the only permitted random source. `random` is forbidden.
