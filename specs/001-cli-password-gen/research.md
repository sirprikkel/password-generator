# Research: CLI Password Generator

**Feature**: `001-cli-password-gen` | **Date**: 2026-02-18
**Status**: Complete — all NEEDS CLARIFICATION resolved

---

## §1 — `secrets.choice()` Uniform Distribution (No Modulo Bias)

**Decision**: Use `secrets.choice(alphabet)` for all character selection.

**Rationale**: Confirmed via CPython source (`Lib/random.py`). `secrets.choice()` delegates to `SystemRandom.choice()` which calls `_randbelow_with_getrandbits(n)`. This method uses **rejection sampling** (draws fresh bits while `r >= n`) — eliminating modulo bias entirely. `SystemRandom` internally uses `os.urandom()` as its entropy source, satisfying FR-008 and Constitution Principle IV.

```python
# CPython _randbelow_with_getrandbits (confirmed):
def _randbelow_with_getrandbits(self, n):
    k = n.bit_length()
    r = self.getrandbits(k)      # OS entropy
    while r >= n:                # rejection sampling
        r = self.getrandbits(k)
    return r
```

**Alternatives considered**: `os.urandom()` with manual modulo rejected — introduces modulo bias. `random.choice()` rejected — uses Mersenne Twister (non-CSPRNG, forbidden by Constitution Principle I).

---

## §2 — `pyperclip` Dependency Audit

**Decision**: Accept `pyperclip >=1.8` (current: 1.11.0, released 2025-09-26) as the single external dependency.

**Rationale**: `pyperclip` is a minimal, widely-used Python clipboard library (~1.1M weekly downloads). No CVEs found via Snyk or Safety CLI for any version. Its threat surface is low: it makes no network calls, reads no user data, and only writes to the OS clipboard. It is justified by SC-005 (cross-platform clipboard without manual user configuration).

**Platform-specific mechanism** (no manual user config required on any platform):
- macOS: `pbcopy`/`pbpaste` — bundled with the OS
- Windows: `ctypes` against the Win32 clipboard API directly — no external tool needed
- Linux: shells out to `xclip` or `xsel` (must be installed); falls back to Qt/KDE mechanisms

**Clipboard failure** raises `pyperclip.PyperclipException`. Every call to `pyperclip.copy()` MUST be wrapped:
```python
try:
    pyperclip.copy(password)
except pyperclip.PyperclipException:
    # print warning to stderr, exit with code 2
```

**Design-level risk (documented)**: On Linux, pyperclip shells out to binaries in PATH. A malicious actor with PATH write access could substitute `xclip`. Low-severity for a local developer tool; documented here per Constitution Principle I.

**Audit checklist** (to be run before release):
- `pip-audit` against `pyperclip` for known CVEs ✓ (run in CI)
- No transitive dependencies — `pyperclip` has no `install_requires` of its own
- Review latest commit activity on GitHub (`asweigart/pyperclip`) before each release

**Alternatives considered**:
- `pywin32` / `pbcopy` / `xclip` natively: platform-specific, defeats SC-005 cross-platform goal.
- `clipboard` (PyPI): less maintained, smaller user base, similar threat surface.
- `xclip`/`xsel` subprocess: Linux-only, not cross-platform.

---

## §3 — CLI Parsing: `argparse` vs `click`

**Decision**: Use Python stdlib `argparse`.

**Rationale**: The CLI surface is minimal (3 flags + `--help`). `argparse` ships with Python, requires no additional installation, and satisfies all requirements. Adding `click` would introduce an unjustified external dependency (Constitution Principle V: Simplicity — each dep must be explicitly justified).

**Alternatives considered**: `click` — more ergonomic but unjustified overhead for this scope. `typer` — adds type annotation dependency, further unjustified.

---

## §4 — `pyproject.toml` Entry Point Pattern

**Decision**: Declare entry point as `passgen = "passgen.cli:main"` under `[project.scripts]`.

**Rationale**: This is the PEP 517/518 standard for installable Python CLI tools. After `pip install .` (or `pip install -e .`), pip creates a `passgen` shim in the environment's `bin/` directory that calls `passgen.cli:main`. No `setup.py` needed.

```toml
[project.scripts]
passgen = "passgen.cli:main"
```

**Alternatives considered**: `setup.py` with `entry_points` — superseded by `pyproject.toml`. Manual `__main__.py` — requires `python -m passgen` invocation, not `passgen` directly.

---

## §5 — Testing Strategy for CSPRNG-Based Code

**Decision**: Test observable behaviour (character set membership, length, invariants) — not randomness itself.

**Rationale**: You cannot deterministically test `secrets` output. Instead, tests verify:
1. **Character set membership**: assert every character in the password belongs to the enabled sets.
2. **Guaranteed characters**: run generator N=100 times; assert each enabled set contributes at least one character on every run.
3. **Length correctness**: assert `len(password) == requested_length`.
4. **Exclusion correctness**: assert no digit appears when `--no-numbers`; assert no symbol when `--no-symbols`.
5. **Non-determinism**: run twice; assert outputs differ (probabilistic, but failure probability ≈ 1/89¹⁶).
6. **Boundary rejection**: assert exit code `1` for length < 8 and > 128.
7. **Stdout/stderr isolation**: capture both streams; assert password value does not appear in stderr.

**CSPRNG usage verification**: The test suite MUST verify that `secrets` is imported and used in `generator.py` (static check) and that `random` is NOT imported.

**Alternatives considered**: Mocking `secrets` — defeats the purpose of testing the CSPRNG path. Statistical tests (chi-square) — too slow and impractical for a unit suite.

---

## §6 — Fisher-Yates Shuffle with CSPRNG

**Decision**: Implement secure shuffle using `secrets.randbelow` in a Fisher-Yates loop.

**Rationale**: `random.shuffle` uses Mersenne Twister (forbidden). Python's `random.SystemRandom().shuffle` is CSPRNG-backed but requires instantiation. The cleanest approach is a standalone function:

```python
import secrets

def secure_shuffle(lst: list) -> None:
    """Fisher-Yates in-place shuffle using secrets.randbelow."""
    for i in range(len(lst) - 1, 0, -1):
        j = secrets.randbelow(i + 1)
        lst[i], lst[j] = lst[j], lst[i]
```

This is explicit, testable, and provably bias-free.

**Alternatives considered**: `sorted(chars, key=lambda _: secrets.token_bytes(4))` — works but less transparent. `random.SystemRandom().shuffle` — requires class instantiation, less readable.
