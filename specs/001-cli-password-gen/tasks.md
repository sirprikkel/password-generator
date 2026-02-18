# Tasks: CLI Password Generator

**Input**: Design documents from `/specs/001-cli-password-gen/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/cli-interface.md ✅, quickstart.md ✅

**Tests**: Included — TDD is **mandatory** per Constitution Principle III and quickstart.md. Write failing tests before every implementation task. Confirm red before green.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and skeleton — no logic yet

- [X] T001 Create `pyproject.toml` with `[project]` metadata (`name = "passgen"`, `version = "0.1.0"`, `requires-python = ">=3.8"`, `dependencies = ["pyperclip>=1.8"]`), `[project.scripts]` entry point (`passgen = "passgen.cli:main"`), `[project.optional-dependencies]` dev group (`pytest`, `pytest-cov`, `ruff`), and `[tool.pytest.ini_options]` (`testpaths = ["tests"]`)
- [X] T002 [P] Create `passgen/__init__.py` with `__version__ = "0.1.0"`
- [X] T003 [P] Create empty `tests/__init__.py`, `tests/unit/__init__.py`, and `tests/integration/__init__.py` as package markers

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core data structures and utilities that ALL user stories depend on — must be complete before any user story begins

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 Write failing unit tests for `CharacterSet` constants (correct character strings, no overlap between sets) and `PasswordConfig` dataclass (defaults: length=16, include_symbols=True, include_numbers=True) in `tests/unit/test_generator.py`
- [X] T005 Create `passgen/generator.py` — define `CharacterSet` string constants (`LOWERCASE = "abcdefghijklmnopqrstuvwxyz"`, `UPPERCASE = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"`, `NUMBERS = "0123456789"`, `SYMBOLS = "!@#$%^&*()-_=+[]{}|;:,.<>?"`) and `PasswordConfig` dataclass with fields `length: int = 16`, `include_symbols: bool = True`, `include_numbers: bool = True`
- [X] T006 Implement `secure_shuffle(lst: list) -> None` in `passgen/generator.py` using Fisher-Yates in-place shuffle with `secrets.randbelow` (forbid `random.shuffle`)
- [X] T007 [P] Create `passgen/clipboard.py` with `copy_to_clipboard(password: str) -> bool` — call `pyperclip.copy(password)` inside a `try/except pyperclip.PyperclipException` block; return `True` on success, `False` on failure (never raises)

**Checkpoint**: Foundation ready — character sets, config, shuffle, and clipboard wrapper are all tested and implemented. User story implementation can now begin.

---

## Phase 3: User Story 1 — Generate Password with Default Settings (Priority: P1) 🎯 MVP

**Goal**: A user runs `passgen` with no arguments and receives a 16-character cryptographically secure password in the terminal, automatically copied to the clipboard, with a confirmation message on stderr.

**Independent Test**: `passgen` with no arguments → password on stdout (16 chars, contains letters/digits/symbols) → `Password copied to clipboard.` on stderr → exit 0.

### Tests for User Story 1

> **⚠️ Write tests FIRST. Run pytest and confirm RED before implementing T011–T013.**

- [X] T008 Write failing unit tests for `generate_password(PasswordConfig())` in `tests/unit/test_generator.py`: assert `len(result) == 16`, all chars in full alphabet (`LOWERCASE + UPPERCASE + NUMBERS + SYMBOLS`), at least one char from each enabled set (run N=100 times), two successive calls return different values
- [X] T009 [P] [US1] Write failing unit tests for `parse_args([])` in `tests/unit/test_cli.py`: assert namespace has `length=16`, `no_symbols=False`, `no_numbers=False`; assert `--help` exits 0
- [X] T010 [P] [US1] Write failing integration test for subprocess invocation `passgen` (no args) in `tests/integration/test_passgen.py`: assert exit code 0, stdout contains exactly a non-empty password string followed by `\n`, stderr contains `"Password copied to clipboard."`, password value does NOT appear in stderr

### Implementation for User Story 1

- [X] T011 [US1] Implement `generate_password(config: PasswordConfig) -> str` in `passgen/generator.py`: build mandatory pool (`LOWERCASE + UPPERCASE`), append optional sets per config flags, guarantee one char per enabled set via `secrets.choice()`, fill remaining `config.length - len(guaranteed)` positions from combined pool, concatenate, call `secure_shuffle()`, return joined string
- [X] T012 [US1] Implement `parse_args(argv=None)` in `passgen/cli.py` using `argparse.ArgumentParser` with program description and `--help`; return parsed namespace (defaults: `length=16`, `no_symbols=False`, `no_numbers=False`)
- [X] T013 [US1] Implement `main()` in `passgen/cli.py`: call `parse_args()` → build `PasswordConfig` → call `generate_password()` → write password to `sys.stdout` → call `copy_to_clipboard()` → write `"Password copied to clipboard.\n"` to `sys.stderr` on success or `"Warning: could not copy to clipboard — paste from terminal output.\n"` on failure → `sys.exit(0)` on success, `sys.exit(2)` on clipboard failure

**Checkpoint**: `passgen` (no args) is fully functional and independently testable. MVP deliverable — stop here to validate.

---

## Phase 4: User Story 2 — Specify Custom Password Length (Priority: P2)

**Goal**: A user passes `--length N` (8–128) to receive a password of exactly N characters. Out-of-range or non-integer values produce a clear error message on stderr and exit code 1 with no password generated.

**Independent Test**: `passgen --length 32` → password on stdout with `len == 32` → exit 0. `passgen --length 4` → empty stdout, error on stderr → exit 1.

### Tests for User Story 2

> **⚠️ Write tests FIRST. Run pytest and confirm RED before implementing T016.**

- [X] T014 [US2] Write failing unit tests for `--length` in `tests/unit/test_cli.py`: assert `parse_args(["--length", "32"])` returns `length=32`; assert `main()` with `--length 4` writes error message to stderr, exits 1, writes nothing to stdout; assert same for `--length 129`; assert `--length abc` exits 1
- [X] T015 [P] [US2] Write failing integration tests in `tests/integration/test_passgen.py`: `passgen --length 32` → exit 0, stdout password has exactly 32 chars; `passgen --length 4` → exit 1, stdout empty, stderr contains `"Error: --length must be at least 8."`; `passgen --length 200` → exit 1, stderr contains `"Error: --length must be at most 128."`

### Implementation for User Story 2

- [X] T016 [US2] Add `--length` argument (`type=int`, `default=16`) to `parse_args()` in `passgen/cli.py`; add post-parse validation in `main()` — if `args.length < 8`: write `"Error: --length must be at least 8.\n"` to stderr and `sys.exit(1)`; if `args.length > 128`: write `"Error: --length must be at most 128.\n"` to stderr and `sys.exit(1)`; propagate validated length to `PasswordConfig(length=args.length)`

**Checkpoint**: `passgen --length N` works correctly for valid and invalid inputs. US1 (no args) still passes all tests.

---

## Phase 5: User Story 3 — Control Character Sets (Priority: P3)

**Goal**: A user passes `--no-symbols` and/or `--no-numbers` to exclude character sets. The generator produces a password using only the remaining enabled sets, still meeting the requested length.

**Independent Test**: `passgen --no-symbols` → password on stdout with no symbol chars → exit 0. `passgen --no-numbers` → password with no digit chars → exit 0.

### Tests for User Story 3

> **⚠️ Write tests FIRST. Run pytest and confirm RED before implementing T020.**

- [X] T017 [US3] Write failing unit tests for `generate_password()` with non-default configs in `tests/unit/test_generator.py`: `PasswordConfig(include_symbols=False)` → no symbol chars in result; `PasswordConfig(include_numbers=False)` → no digit chars; `PasswordConfig(include_symbols=False, include_numbers=False)` → only letters; all three cases still produce correct length; at least one lowercase and one uppercase always present
- [X] T018 [P] [US3] Write failing unit tests for `--no-symbols` and `--no-numbers` flag parsing in `tests/unit/test_cli.py`: `parse_args(["--no-symbols"])` returns `no_symbols=True`; `parse_args(["--no-numbers"])` returns `no_numbers=True`; `parse_args(["--no-symbols", "--no-numbers"])` returns both True
- [X] T019 [P] [US3] Write failing integration tests in `tests/integration/test_passgen.py`: `passgen --no-symbols` → exit 0, password contains no chars from `SYMBOLS`; `passgen --no-numbers` → exit 0, password contains no chars from `NUMBERS`; `passgen --no-symbols --no-numbers` → exit 0, password contains only chars from `LOWERCASE + UPPERCASE`

### Implementation for User Story 3

- [X] T020 [US3] Add `--no-symbols` and `--no-numbers` store-true flags to `parse_args()` in `passgen/cli.py`; update `main()` to pass `include_symbols=not args.no_symbols` and `include_numbers=not args.no_numbers` to `PasswordConfig`

**Checkpoint**: All three user stories are independently functional. `generate_password()` correctly handles all PasswordConfig combinations.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Security hardening, invariant tests, linting, and end-to-end validation

- [X] T021 [P] Add CSPRNG static verification test in `tests/unit/test_generator.py`: open `passgen/generator.py` as text, assert `"import secrets"` is present, assert `"import random"` is absent; this enforces the CSPRNG mandate from Constitution Principle I and research.md §1
- [X] T022 [P] Add stdout/stderr isolation and invariants tests in `tests/unit/test_cli.py`: for every exit-code scenario (0, 1, 2), capture both streams and assert the generated password value does NOT appear in stderr; assert stderr is non-empty for exit codes 1 and 2; assert stdout contains ONLY the password + newline for exit code 0 or 2
- [X] T023 Run `ruff check .` from the repo root and fix any linting errors in `passgen/`
- [X] T024 Validate all `quickstart.md` scenarios end-to-end: `pip install -e ".[dev]"`, run `passgen`, `passgen --length 32`, `passgen --no-symbols`, `passgen --no-numbers`, `passgen --no-symbols --no-numbers`, `passgen --length 4` (expect exit 1); confirm `pytest --cov=passgen --cov-report=term-missing` passes with no failures

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 completion — **BLOCKS all user stories**
- **User Stories (Phase 3–5)**: All depend on Phase 2 completion
  - US1 (Phase 3): No dependency on US2 or US3
  - US2 (Phase 4): Depends on Phase 3 (extends cli.py main())
  - US3 (Phase 5): Depends on Phase 3 (extends cli.py main()); uses generator already written in US1
- **Polish (Phase 6)**: Depends on all user story phases complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Phase 2 — no story dependencies
- **User Story 2 (P2)**: Should start after US1 (extends `main()` in `passgen/cli.py`)
- **User Story 3 (P3)**: Should start after US1 (extends `main()` in `passgen/cli.py`); US3 generator behavior is already implemented in US1's `generate_password()`

### Within Each Phase

- Tests MUST be written first and MUST fail before any implementation begins (Red-Green-Refactor)
- Within foundational phase: T005 → T006 → T007 (all generator.py, sequential); T007 can run parallel with T005/T006 (clipboard.py)
- Within US1: T008/T009/T010 all [P] (different files) → T011 → T012 → T013 (cli.py sequential)
- Within US2: T014/T015 [P] → T016
- Within US3: T017/T018/T019 all [P] → T020

### Parallel Opportunities

- Phase 1: T002 and T003 can run parallel to each other
- Phase 2: T007 (clipboard.py) can run parallel to T005+T006 (generator.py)
- Phase 3 tests: T008, T009, T010 can all run in parallel (different files)
- Phase 4 tests: T014 and T015 can run in parallel (different files)
- Phase 5 tests: T017, T018, T019 can all run in parallel (different files)
- Phase 6: T021 and T022 can run in parallel (different files)

---

## Parallel Example: User Story 1 (Phase 3)

```bash
# Step 1 — Write all failing tests in parallel (different files, no shared state):
Task A: "Write failing unit tests for generate_password() in tests/unit/test_generator.py"   # T008
Task B: "Write failing unit tests for parse_args() in tests/unit/test_cli.py"                 # T009
Task C: "Write failing integration test in tests/integration/test_passgen.py"                 # T010

# Verify: run pytest → confirm ALL new tests RED

# Step 2 — Implement (generator.py → cli.py, sequential):
Task D: "Implement generate_password() in passgen/generator.py"    # T011
Task E: "Implement parse_args() in passgen/cli.py"                 # T012
Task F: "Implement main() in passgen/cli.py"                       # T013

# Verify: run pytest → confirm ALL tests GREEN
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL — blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: `passgen` works with no arguments — password on stdout, confirmation on stderr, clipboard populated
5. Deploy / demo MVP

### Incremental Delivery

1. Phase 1 + Phase 2 → skeleton + core engine ready
2. Phase 3 → `passgen` works (MVP — 16-char password, full char sets, clipboard)
3. Phase 4 → `passgen --length N` works
4. Phase 5 → `passgen --no-symbols --no-numbers` works
5. Phase 6 → hardened, linted, validated

### Parallel Team Strategy

With two developers:

1. Both complete Phase 1 + Phase 2 together
2. Once Phase 3 is done (US1 baseline):
   - Developer A: User Story 2 (--length)
   - Developer B: User Story 3 (--no-symbols / --no-numbers)
3. Note: US2 and US3 both touch `passgen/cli.py` `main()` — coordinate to avoid merge conflicts

---

## Notes

- `[P]` tasks = different files, no dependencies on incomplete tasks in the same phase
- `[US#]` label maps each task to a specific user story for independent traceability
- TDD is **mandatory** — every implementation task must have a RED test before it turns GREEN
- Password value must never appear in stderr — verified by T010, T015, T019, T022
- `secrets` module is the only permitted random source — verified by T021 (static check)
- Stop at any checkpoint to validate the completed story independently before moving to the next
- Run `pytest --cov=passgen` after each phase to confirm coverage is not regressing
- Commit after each task or logical group; branch: `001-cli-password-gen`
