# Feature Specification: CLI Password Generator

**Feature Branch**: `001-cli-password-gen`
**Created**: 2026-02-18
**Status**: Draft
**Input**: User description: "Bouw een CLI tool die veilige wachtwoorden genereert. De gebruiker moet via argumenten de lengte kunnen bepalen en kunnen kiezen of er symbolen en cijfers gebruikt worden. Na generatie moet het wachtwoord automatisch naar het clipboard gekopieerd worden en moet er een bevestiging in de terminal verschijnen."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Generate Password with Default Settings (Priority: P1)

A user runs the tool without any arguments and receives a secure password that is immediately ready to use. The password is automatically copied to the clipboard, and a confirmation message tells the user the operation succeeded.

**Why this priority**: This is the core capability. Without a working default flow, no other story delivers value. It represents the minimum viable product.

**Independent Test**: Run the tool with no arguments; verify a password appears in the terminal and the clipboard contains the same password.

**Acceptance Scenarios**:

1. **Given** the tool is installed, **When** the user runs it with no arguments, **Then** a password of the default length (16 characters) is generated using letters, numbers, and symbols, displayed in the terminal, copied to the clipboard, and a confirmation message is shown.
2. **Given** the tool is run with no arguments, **When** the password is generated, **Then** every run produces a different password (non-deterministic output).
3. **Given** the tool completes successfully, **When** the user checks the clipboard, **Then** it contains exactly the generated password with no extra whitespace or newlines.

---

### User Story 2 - Specify Custom Password Length (Priority: P2)

A user needs a password of a specific length for a service with particular requirements. They pass a length argument to the tool and receive a password of exactly that length.

**Why this priority**: Length control is a fundamental customization that directly affects compatibility with target services. It builds directly on the P1 story.

**Independent Test**: Run the tool with `--length 24`; verify the output password is exactly 24 characters long.

**Acceptance Scenarios**:

1. **Given** the tool is installed, **When** the user runs it with `--length 32`, **Then** the generated password is exactly 32 characters long.
2. **Given** a length argument is provided, **When** the length is below the minimum allowed value (8), **Then** the tool displays a clear error message explaining the minimum length and exits without generating a password.
3. **Given** a length argument is provided, **When** the length is above the maximum allowed value (128), **Then** the tool displays a clear error message explaining the maximum length and exits without generating a password.
4. **Given** a non-numeric value is passed as length, **When** the tool starts, **Then** it displays a usage error and exits without generating a password.

---

### User Story 3 - Control Character Sets (Priority: P3)

A user needs a password that excludes symbols (e.g., for a system that does not accept special characters) or excludes numbers. They use flags to disable specific character sets, and the tool generates a password using only the allowed characters.

**Why this priority**: Character set control increases compatibility with restrictive systems. It depends on the core generation flow being in place.

**Independent Test**: Run the tool with `--no-symbols`; verify the output contains no symbol characters. Run with `--no-numbers`; verify the output contains no digit characters.

**Acceptance Scenarios**:

1. **Given** the tool is run with `--no-symbols`, **When** a password is generated, **Then** the password contains only letters and numbers.
2. **Given** the tool is run with `--no-numbers`, **When** a password is generated, **Then** the password contains only letters and symbols.
3. **Given** the tool is run with both `--no-symbols` and `--no-numbers`, **When** a password is generated, **Then** the password contains only letters.
4. **Given** both symbols and numbers are disabled, **When** the tool generates a password, **Then** the password still meets the requested length using only letters.
5. **Given** no flags are provided, **When** a password is generated, **Then** symbols and numbers are both included by default.

---

### Edge Cases

- What happens when the requested length is 0 or negative? The tool must reject it with a clear error message.
- What happens when the clipboard is unavailable (e.g., headless server, no display)? The tool displays a warning that the clipboard copy failed, but still prints the generated password to the terminal so the user can retrieve it manually.
- What happens when only one character set remains after disabling symbols and numbers? The tool generates a letters-only password and continues normally.
- What happens when the requested length is extremely large (e.g., 10,000)? The tool enforces a maximum of 128 characters and shows an error.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The tool MUST accept an optional `--length` argument specifying the number of characters in the generated password.
- **FR-002**: The tool MUST use a default length of 16 characters when no `--length` argument is provided.
- **FR-003**: The tool MUST enforce a minimum password length of 8 characters and a maximum of 128 characters.
- **FR-004**: The tool MUST accept a `--no-symbols` flag to exclude special/symbol characters from the generated password.
- **FR-005**: The tool MUST accept a `--no-numbers` flag to exclude numeric characters from the generated password.
- **FR-006**: The tool MUST include both symbols and numbers in generated passwords by default (opt-out model).
- **FR-007**: The tool MUST always include at least lowercase and uppercase letters in any generated password. Additionally, every other enabled character set (numbers, symbols) MUST each contribute at least one character to the generated password. Remaining positions are filled from the combined pool of enabled sets, then the full password is shuffled using a cryptographically secure shuffle.
- **FR-008**: The tool MUST use a cryptographically secure random source to generate passwords.
- **FR-009**: The tool MUST automatically copy the generated password to the system clipboard after generation. If the clipboard is unavailable, the tool MUST display a warning message but still print the password to the terminal and exit successfully.
- **FR-010**: The tool MUST write the generated password to `stdout`. All other output (confirmation messages, warnings, errors) MUST be written to `stderr`. This enables composable use (e.g., `passgen | xclip`).
- **FR-011**: The tool MUST write a confirmation message to `stderr` confirming the password was copied to the clipboard.
- **FR-012**: The tool MUST write a clear, human-readable error message to `stderr` when invalid arguments are provided, and exit without generating a password.
- **FR-013**: The tool MUST provide a `--help` flag that describes available arguments and their defaults.
- **FR-014**: The tool MUST exit with the following codes: `0` — password generated and copied to clipboard successfully; `1` — invalid or out-of-range arguments (no password generated); `2` — password generated and printed, but clipboard copy failed.

### Key Entities

- **Password**: A generated string with configurable length and character composition. Attributes: length (number of characters), character sets used (letters, numbers, symbols), value (the generated string).
- **Character Set**: A named group of characters eligible for inclusion in a password. Types: lowercase letters, uppercase letters, numbers, symbols.
- **CLI Arguments**: User-provided inputs that control password generation. Attributes: length value, symbol inclusion flag, number inclusion flag.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A user can generate a password ready to paste into any application in under 2 seconds from the moment they run the command.
- **SC-002**: 100% of generated passwords contain only characters from the explicitly requested character sets.
- **SC-003**: The generated password is available in the clipboard immediately after the confirmation message is displayed, requiring no additional user action.
- **SC-004**: Invalid or out-of-range arguments always produce an informative error message — zero silent failures.
- **SC-005**: The tool works correctly across all major operating systems (macOS, Linux, Windows) without requiring manual clipboard configuration by the user.

## Assumptions

- Default password length of 16 characters is appropriate for general use.
- Symbols are defined as printable non-alphanumeric ASCII characters (e.g., `!@#$%^&*()-_=+[]{}|;:,.<>?`).
- Lowercase and uppercase letters are always included and cannot be disabled, ensuring baseline password strength.
- The tool targets developer and power-user audiences comfortable with a terminal interface.
- A single password is generated per invocation; batch generation is out of scope.
- The tool does not store, log, or transmit generated passwords anywhere other than the terminal output and clipboard.

## Constraints & Tradeoffs

- **Implementation language**: Python. Uses the standard `secrets` module to satisfy FR-008 (cryptographically secure randomness). Cross-platform clipboard access via the `pyperclip` library to satisfy SC-005.
- **Distribution format**: Installable Python package using `pyproject.toml`. After `pip install`, the tool is invocable as `passgen` via a declared entry point. Python 3.8+ is the minimum required runtime.

## Clarifications

### Session 2026-02-18

- Q: What programming language/runtime should be used to implement the CLI tool? → A: Python (using `secrets` for cryptographic randomness and `pyperclip` for clipboard)
- Q: Must every enabled character set contribute at least one character to the generated password? → A: Yes — guaranteed minimum one character per enabled set; remaining positions filled from combined pool, then shuffled securely
- Q: Should the password and status messages use separate output streams? → A: Yes — password to `stdout`, all other messages (confirmation, warnings, errors) to `stderr`
- Q: What exit codes should the tool use? → A: `0` full success, `1` invalid/out-of-range arguments, `2` clipboard failure (password still printed to stdout)
- Q: How should the tool be distributed and invoked? → A: Installable Python package (`pyproject.toml` + entry point); invoked as `passgen` after `pip install`
