# CLI Interface Contract: `passgen`

**Feature**: `001-cli-password-gen` | **Date**: 2026-02-18

---

## Invocation

```
passgen [--length N] [--no-symbols] [--no-numbers] [--help]
```

---

## Arguments

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `--length N` | `int` | `16` | Number of characters in the generated password. Must be 8–128 inclusive. |
| `--no-symbols` | flag | not set (symbols included) | Exclude symbol characters from the password. |
| `--no-numbers` | flag | not set (numbers included) | Exclude numeric characters from the password. |
| `--help` / `-h` | flag | — | Display help text and exit `0`. |

---

## Output Protocol

### stdout
Receives **only** the generated password, followed by a newline.

```
<password>\n
```

**Invariants**:
- Contains exactly the password value and one trailing newline.
- Never contains confirmation messages, warnings, or errors.
- Clipboard copy result does NOT affect stdout.

### stderr
Receives all human-readable messages.

**On success (exit 0)**:
```
Password copied to clipboard.
```

**On clipboard failure (exit 2)**:
```
Warning: could not copy to clipboard — paste from terminal output.
```

**On argument error (exit 1)** — examples:
```
Error: --length must be at least 8.
Error: --length must be at most 128.
Error: --length requires an integer value.
```

**Invariants for stderr**:
- MUST NOT contain the password value under any circumstances.
- MUST NOT be empty when exit code is 1 or 2.

---

## Exit Codes

| Code | Meaning | stdout | stderr |
|------|---------|--------|--------|
| `0` | Success: password generated and copied to clipboard | password | confirmation |
| `1` | Argument error: no password generated | empty | error message |
| `2` | Partial success: password generated, clipboard failed | password | warning |

---

## Examples

**Default usage**:
```sh
$ passgen
# stdout: Kp3!mQxZ9@vLrY2w
# stderr: Password copied to clipboard.
# exit:   0
```

**Custom length**:
```sh
$ passgen --length 32
# stdout: <32-char password>
# stderr: Password copied to clipboard.
# exit:   0
```

**Letters and symbols only (no numbers)**:
```sh
$ passgen --no-numbers
# stdout: <password with no digits>
# stderr: Password copied to clipboard.
# exit:   0
```

**Letters only**:
```sh
$ passgen --no-symbols --no-numbers
# stdout: <letters-only password>
# stderr: Password copied to clipboard.
# exit:   0
```

**Invalid length (too short)**:
```sh
$ passgen --length 4
# stdout: (empty)
# stderr: Error: --length must be at least 8.
# exit:   1
```

**Composable with xclip (manual clipboard)**:
```sh
$ passgen | xclip -selection clipboard
```

---

## Character Set Definitions

| Set | Characters |
|-----|-----------|
| Lowercase | `a-z` (26 chars) |
| Uppercase | `A-Z` (26 chars) |
| Numbers | `0-9` (10 chars) |
| Symbols | `!@#$%^&*()-_=+[]{}|;:,.<>?` (27 chars) |

**Default alphabet** (all sets): 89 characters → log₂(89¹⁶) ≈ 104.8 bits entropy.

---

## Constraints

- One password per invocation. Batch generation is out of scope.
- No stdin is read.
- No network requests are made.
- No password values appear in any output channel other than stdout.
