"""Integration tests for passgen CLI — subprocess invocation end-to-end."""
import subprocess
import sys
import os

# Path to the venv python so the installed `passgen` script is found
PYTHON = sys.executable


def run_passgen(*args, env=None):
    """Run passgen as a subprocess, return (returncode, stdout, stderr)."""
    base_env = {**os.environ}
    if env:
        base_env.update(env)
    # Force clipboard to fail gracefully in headless CI by unsetting DISPLAY
    # but allow tests to override via env parameter.
    result = subprocess.run(
        [PYTHON, "-m", "passgen.cli"] + list(args),
        capture_output=True,
        text=True,
        env=base_env,
    )
    return result.returncode, result.stdout, result.stderr


# ---------------------------------------------------------------------------
# T010 — US1: passgen with no arguments
# ---------------------------------------------------------------------------

class TestPassgenNoArgs:
    def test_exit_code_0_or_2(self):
        """Exit 0 (clipboard ok) or 2 (no display/clipboard) — never 1."""
        code, stdout, stderr = run_passgen()
        assert code in (0, 2)

    def test_stdout_contains_nonempty_password(self):
        code, stdout, stderr = run_passgen()
        password = stdout.strip()
        assert password != ""

    def test_stdout_ends_with_newline(self):
        code, stdout, stderr = run_passgen()
        assert stdout.endswith("\n")

    def test_stdout_exactly_password_newline(self):
        code, stdout, stderr = run_passgen()
        # stdout should be exactly the password + one newline
        assert stdout.count("\n") == 1

    def test_default_password_length_16(self):
        code, stdout, stderr = run_passgen()
        password = stdout.strip()
        assert len(password) == 16

    def test_password_not_in_stderr(self):
        code, stdout, stderr = run_passgen()
        password = stdout.strip()
        assert password not in stderr

    def test_stderr_contains_message(self):
        code, stdout, stderr = run_passgen()
        # Either clipboard success or clipboard failure message on stderr
        assert stderr.strip() != ""


# ---------------------------------------------------------------------------
# T015 — US2: passgen --length N
# ---------------------------------------------------------------------------

class TestPassgenLength:
    def test_length_32_exit_0_or_2(self):
        code, stdout, stderr = run_passgen("--length", "32")
        assert code in (0, 2)

    def test_length_32_password_has_32_chars(self):
        code, stdout, stderr = run_passgen("--length", "32")
        assert len(stdout.strip()) == 32

    def test_length_4_exit_1(self):
        code, stdout, stderr = run_passgen("--length", "4")
        assert code == 1

    def test_length_4_stdout_empty(self):
        code, stdout, stderr = run_passgen("--length", "4")
        assert stdout == ""

    def test_length_4_stderr_contains_error(self):
        code, stdout, stderr = run_passgen("--length", "4")
        assert "Error: --length must be at least 8." in stderr

    def test_length_200_exit_1(self):
        code, stdout, stderr = run_passgen("--length", "200")
        assert code == 1

    def test_length_200_stderr_contains_error(self):
        code, stdout, stderr = run_passgen("--length", "200")
        assert "Error: --length must be at most 128." in stderr


# ---------------------------------------------------------------------------
# T019 — US3: passgen --no-symbols / --no-numbers
# ---------------------------------------------------------------------------

SYMBOLS = "!@#$%^&*()-_=+[]{}|;:,.<>?"
NUMBERS = "0123456789"
LOWERCASE = "abcdefghijklmnopqrstuvwxyz"
UPPERCASE = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


class TestPassgenCharSets:
    def test_no_symbols_exit_0_or_2(self):
        code, stdout, stderr = run_passgen("--no-symbols")
        assert code in (0, 2)

    def test_no_symbols_password_no_symbol_chars(self):
        code, stdout, stderr = run_passgen("--no-symbols")
        password = stdout.strip()
        for ch in password:
            assert ch not in SYMBOLS

    def test_no_numbers_exit_0_or_2(self):
        code, stdout, stderr = run_passgen("--no-numbers")
        assert code in (0, 2)

    def test_no_numbers_password_no_digit_chars(self):
        code, stdout, stderr = run_passgen("--no-numbers")
        password = stdout.strip()
        for ch in password:
            assert ch not in NUMBERS

    def test_no_symbols_no_numbers_exit_0_or_2(self):
        code, stdout, stderr = run_passgen("--no-symbols", "--no-numbers")
        assert code in (0, 2)

    def test_no_symbols_no_numbers_letters_only(self):
        code, stdout, stderr = run_passgen("--no-symbols", "--no-numbers")
        password = stdout.strip()
        letters = LOWERCASE + UPPERCASE
        for ch in password:
            assert ch in letters
