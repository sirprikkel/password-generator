<!--
  SYNC IMPACT REPORT
  ==================
  Version change: (template) → 1.0.0 (initial ratification)

  Modified principles: N/A — first instantiation from template.

  Added sections:
    - Core Principles (5 defined: I. Security-First, II. CLI Interface,
      III. Test-First, IV. Cryptographic Correctness, V. Simplicity)
    - Security Requirements
    - Development Workflow
    - Governance

  Removed sections: N/A

  Templates reviewed:
    ✅ .specify/templates/plan-template.md      — Constitution Check gate present;
                                                  aligns with Security-First and
                                                  Test-First gates. No changes needed.
    ✅ .specify/templates/spec-template.md      — Mandatory sections (User Scenarios,
                                                  Requirements, Success Criteria) align
                                                  with Test-First and Security-First.
                                                  No changes needed.
    ⚠  .specify/templates/tasks-template.md    — NOTE: Template states "Tests are
                                                  OPTIONAL". This conflicts with
                                                  Principle III (Test-First,
                                                  NON-NEGOTIABLE). Recommend updating
                                                  the note for this project to reflect
                                                  that tests are mandatory.
    ✅ .specify/templates/checklist-template.md — Generic template; no
                                                  constitution-specific references.
    ✅ .specify/templates/agent-file-template.md — Generic template; no
                                                   constitution-specific references.

  Follow-up TODOs:
    - ⚠ tasks-template.md: Consider updating the "Tests are OPTIONAL" note to reflect
      the Test-First mandate for this project (Principle III).
-->

# Password Generator Constitution

## Core Principles

### I. Security-First

Password generation is a security-critical operation. All implementations MUST adhere to
the following non-negotiable rules:

- Cryptographically Secure Pseudo-Random Number Generation (CSPRNG) MUST be used for all
  password generation. Platform-native entropy sources (e.g., `crypto.getRandomValues`,
  `os.urandom`, `SecureRandom`) are required. Use of `Math.random()` or any equivalent
  non-cryptographic RNG is FORBIDDEN.
- Generated passwords MUST NOT be written to logs, debug output, or any persistent store
  beyond the intended output channel (stdout or the caller's return value).
- All user-supplied inputs (charset overrides, length parameters, flags) MUST be validated
  and rejected with a clear error message if out of accepted bounds.
- Any feature with a potential security impact MUST include a threat model note in the
  spec before implementation begins.

**Rationale**: The sole purpose of this tool is to generate passwords users will rely on
for real security. Any cryptographic weakness undermines the entire value proposition.

### II. CLI Interface

The password generator MUST expose all functionality through a command-line interface.

- Text I/O protocol: arguments/stdin → stdout for output; all errors → stderr.
- MUST support human-readable (plain text) output as the default.
- SHOULD support machine-readable output (e.g., `--json` flag) for scripting and
  integration use cases.
- Exit codes MUST be meaningful: `0` on success, non-zero on any error.

**Rationale**: A CLI interface ensures the tool composes with other Unix tools, works in
scripts and CI pipelines, and can be tested without a GUI dependency.

### III. Test-First (NON-NEGOTIABLE)

Test-Driven Development is MANDATORY for all features without exception.

- Tests MUST be written and confirmed failing (Red) before any implementation code is
  written.
- The Red-Green-Refactor cycle MUST be strictly followed.
- No feature branch MUST be merged unless all tests pass.
- Unit tests MUST cover: character set validation, length boundary constraints, entropy
  calculations, CSPRNG usage verification, and absence of password leakage in outputs.

**Rationale**: For a security tool, correctness is non-negotiable. TDD ensures edge cases
and security constraints are captured as executable specifications first.

### IV. Cryptographic Correctness

All randomness and entropy operations MUST be provably correct.

- Character selection MUST guarantee uniform distribution across the requested character
  set. Modulo bias MUST be eliminated (e.g., via rejection sampling or equivalent
  technique).
- Entropy estimates (bits of entropy per generated password) MUST be calculable and
  surfaceable to the user on request.
- Any deviation from uniform distribution MUST be detected by tests and treated as a
  security defect, not a cosmetic issue.

**Rationale**: A password generator that introduces statistical bias weakens passwords in
ways invisible to users. Uniformity is a security property, not merely a quality attribute.

### V. Simplicity

Complexity MUST be justified by an explicit, present requirement.

- YAGNI: features MUST NOT be added speculatively or for anticipated future use.
- Prefer the simplest implementation that fully satisfies stated requirements.
- External dependencies MUST be minimized; each MUST be explicitly justified in the plan.
- No abstraction layer MUST be introduced unless it serves at least two concrete use cases
  within this project.

**Rationale**: Unnecessary complexity increases attack surface and maintenance burden. For
a security tool, simpler is demonstrably safer.

## Security Requirements

- All random number generation MUST use OS-provided entropy sources exclusively.
- The tool MUST NOT make network requests of any kind during password generation.
- No telemetry, analytics, or usage tracking of any kind is permitted.
- Generated passwords MUST be zeroized from memory where the runtime allows it.
- All dependencies MUST be audited for known CVEs before inclusion. A dependency with an
  unpatched critical CVE MUST NOT be shipped.
- Password values MUST go exclusively to stdout. All other output channels (stderr, logs,
  debug output) MUST be sanitized to never contain password values.

## Development Workflow

- All new features MUST have an approved `spec.md` before implementation begins.
- The `plan.md` MUST include a Constitution Check section that explicitly verifies
  compliance with Principles I–V before Phase 0 research begins.
- Code review MUST verify: CSPRNG usage, absence of password logging, adequate test
  coverage of security constraints, and absence of unjustified dependencies.
- A feature is DONE only when: all tests pass, the spec's acceptance scenarios are met,
  and no password values appear in any log or debug output.
- `tasks.md` MUST be generated from `plan.md` before implementation starts, and tests
  MUST appear before implementation tasks within each user story phase.

## Governance

This constitution supersedes all other development practices for the Password Generator
project. Amendments require:

1. A written proposal describing the change and motivation.
2. A version bump following the versioning policy below.
3. An updated Sync Impact Report prepended to this file.
4. Review of all affected templates and dependent artifacts.

**Versioning policy**:

- MAJOR: Removal or redefinition of an existing principle, or governance restructure.
- MINOR: New principle, new mandatory section, or materially expanded guidance added.
- PATCH: Clarifications, wording improvements, typo fixes, non-semantic refinements.

**Compliance**: All PRs and reviews MUST verify compliance with this constitution. Any
violation MUST be remediated before merge, or documented as a justified exception in the
Complexity Tracking table of the relevant `plan.md`.

**Version**: 1.0.0 | **Ratified**: 2026-02-18 | **Last Amended**: 2026-02-18
