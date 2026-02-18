# Implementation Plan: CLI Password Generator

**Branch**: `001-cli-password-gen` | **Date**: 2026-02-18 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-cli-password-gen/spec.md`

## Summary

Build a cross-platform Python CLI tool (`passgen`) that generates cryptographically secure passwords. The tool accepts optional `--length`, `--no-symbols`, and `--no-numbers` flags, writes the generated password to `stdout`, copies it to the system clipboard via `pyperclip`, and emits confirmation/error messages to `stderr`. Exit codes: `0` success, `1` argument error, `2` clipboard failure. Distributed as an installable `pyproject.toml` package.

## Technical Context

**Language/Version**: Python 3.8+
**Primary Dependencies**: `secrets` (stdlib, CSPRNG), `argparse` (stdlib, CLI parsing), `pyperclip` ^1.8 (cross-platform clipboard)
**Storage**: N/A
**Testing**: pytest + pytest-cov
**Target Platform**: macOS, Linux, Windows (cross-platform CLI)
**Project Type**: Single
**Performance Goals**: < 2 seconds end-to-end (SC-001)
**Constraints**: No network requests; no password in logs/stderr/debug output; no telemetry; Python 3.8+ minimum runtime

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Check | Status | Notes |
|-----------|-------|--------|-------|
| **I. Security-First** | CSPRNG via `secrets` stdlib; no password in logs; all inputs validated; threat model in data-model.md | ✅ PASS | Threat model documented in data-model.md |
| **II. CLI Interface** | `stdout` for password only; `stderr` for all messages; exit codes `0`/`1`/`2`; `--help` flag | ✅ PASS | Matches FR-010, FR-014 |
| **III. Test-First** | pytest mandatory; tests written before implementation; Red-Green-Refactor enforced in tasks.md | ✅ PASS | tests/ directory; tasks.md will order tests before impl |
| **IV. Cryptographic Correctness** | `secrets.choice()` uses rejection sampling internally — no modulo bias; uniform distribution guaranteed | ✅ PASS | See research.md §1 |
| **V. Simplicity** | 1 external dep (`pyperclip`, justified by SC-005 cross-platform requirement); no speculative features | ✅ PASS | See research.md §2 |

**Result**: All gates PASS. Proceed to Phase 0.

*Post-Phase 1 re-check*: Design in data-model.md and contracts/ introduces no new principles violations. Password value never appears in contract error shapes or log output. Constitution Check confirmed PASS.

## Project Structure

### Documentation (this feature)

```text
specs/001-cli-password-gen/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   └── cli-interface.md
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
passgen/
├── __init__.py          # package metadata (version)
├── cli.py               # argparse entrypoint; orchestrates generation + clipboard
├── generator.py         # password generation logic (secrets, character sets)
└── clipboard.py         # pyperclip wrapper; isolates clipboard side-effect

tests/
├── unit/
│   ├── test_generator.py   # character set constraints, length, shuffle, edge cases
│   └── test_cli.py         # argument parsing, exit codes, stdout/stderr routing
└── integration/
    └── test_passgen.py     # end-to-end invocation via subprocess

pyproject.toml
```

**Structure Decision**: Single-project layout. No backend/frontend split needed. `passgen/` is the importable package; `tests/` mirrors package structure. CLI entrypoint declared in `pyproject.toml` as `passgen = "passgen.cli:main"`.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations. Table omitted.
