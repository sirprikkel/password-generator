# Data Model: CLI Password Generator

**Feature**: `001-cli-password-gen` | **Date**: 2026-02-18

---

## Threat Model

*Required by Constitution Principle I before implementation.*

| Threat | Vector | Mitigation |
|--------|--------|------------|
| Weak passwords from non-CSPRNG source | Using `random` instead of `secrets` | `secrets` module mandated; static analysis / test verifies import |
| Password leakage in stderr/logs | Debug prints, error messages including password value | Password value flows only through: generator return → stdout write → clipboard. Never touches stderr. Tests assert stderr contains no password value. |
| Clipboard poisoning by malicious pre-copy content | Not a tool concern; tool only writes to clipboard | Out of scope |
| Length manipulation via environment | User provides `--length` | Boundary validation: min 8, max 128; argparse `type=int` |
| Modulo bias in character selection | Using `%` on `os.urandom` bytes | `secrets.choice()` uses rejection sampling internally; no modulo bias |
| Clipboard data persistence | OS clipboard history tools may retain password | Documented limitation; out of scope for this tool |

---

## Entities

### 1. `PasswordConfig`

Represents the validated user intent for a password generation request. Created by the CLI layer from parsed arguments.

| Field | Type | Default | Constraints |
|-------|------|---------|-------------|
| `length` | `int` | `16` | 8 ≤ length ≤ 128 |
| `include_symbols` | `bool` | `True` | — |
| `include_numbers` | `bool` | `True` | — |

**Validation rules**:
- `length < 8` → reject, exit code `1`, message: `"Error: --length must be at least 8"`
- `length > 128` → reject, exit code `1`, message: `"Error: --length must be at most 128"`
- `length` not an integer → argparse rejects automatically, exit code `1`
- All combinations of `include_symbols`/`include_numbers` are valid (letters always included)

---

### 2. `CharacterSet`

Named groups of characters eligible for password composition.

| Name | Characters | Always Included |
|------|-----------|-----------------|
| `LOWERCASE` | `abcdefghijklmnopqrstuvwxyz` | Yes |
| `UPPERCASE` | `ABCDEFGHIJKLMNOPQRSTUVWXYZ` | Yes |
| `NUMBERS` | `0123456789` | No (opt-out via `--no-numbers`) |
| `SYMBOLS` | `!@#$%^&*()-_=+[]{}|;:,.<>?` | No (opt-out via `--no-symbols`) |

**Note**: Symbols are printable non-alphanumeric ASCII as defined in spec Assumptions.

---

### 3. `Password`

The output entity produced by the generator.

| Field | Type | Description |
|-------|------|-------------|
| `value` | `str` | The generated password string |
| `length` | `int` | Exact character count (equals `PasswordConfig.length`) |
| `character_sets_used` | `list[str]` | Names of `CharacterSet` groups that contributed characters |

**Invariants** (all must hold on every generated password):
- `len(value) == length`
- `LOWERCASE` and `UPPERCASE` always in `character_sets_used`
- If `include_numbers=True` → at least 1 digit in `value`; `NUMBERS` in `character_sets_used`
- If `include_symbols=True` → at least 1 symbol in `value`; `SYMBOLS` in `character_sets_used`
- All characters in `value` belong to the union of enabled character sets
- `value` is produced by a cryptographically secure shuffle (FR-007, FR-008)

---

### 4. `ExitCode`

Enumerated exit codes for the CLI process.

| Code | Name | Condition |
|------|------|-----------|
| `0` | `SUCCESS` | Password generated and copied to clipboard successfully |
| `1` | `ARG_ERROR` | Invalid or out-of-range arguments; no password generated |
| `2` | `CLIPBOARD_ERROR` | Password generated and printed to stdout; clipboard copy failed |

---

## Generation Algorithm

```
function generate_password(config: PasswordConfig) -> Password:
  # 1. Build mandatory pool
  pool = LOWERCASE + UPPERCASE

  # 2. Add optional sets
  optional_sets = []
  if config.include_numbers:
    optional_sets.append(NUMBERS)
  if config.include_symbols:
    optional_sets.append(SYMBOLS)

  # 3. Seed with one guaranteed character per enabled set
  guaranteed = [secrets.choice(LOWERCASE), secrets.choice(UPPERCASE)]
  for charset in optional_sets:
    guaranteed.append(secrets.choice(charset))
    pool += charset

  # 4. Fill remaining positions from combined pool
  remaining = config.length - len(guaranteed)
  filler = [secrets.choice(pool) for _ in range(remaining)]

  # 5. Cryptographically secure shuffle of all characters
  chars = guaranteed + filler
  secrets_shuffle(chars)   # see note below

  return Password(value=''.join(chars), ...)
```

**Note on `secrets_shuffle`**: Python's `random.shuffle` uses the Mersenne Twister (non-CSPRNG). A compliant implementation uses `secrets.randbelow` to implement Fisher-Yates in-place shuffle, or uses `sorted(chars, key=lambda _: secrets.token_bytes(4))`. Either satisfies FR-008.

---

## State Transitions

No persistent state. Single invocation flow:

```
START → parse_args → [validate] →
  [invalid] → stderr(error) → exit(1)
  [valid]   → generate_password → stdout(password) →
               [clipboard_ok]   → stderr(confirmation) → exit(0)
               [clipboard_fail] → stderr(warning)      → exit(2)
```
