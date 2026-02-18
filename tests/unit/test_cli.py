"""Unit tests for passgen.cli — TDD: tests written before implementation."""
import pytest


# ---------------------------------------------------------------------------
# T009 — parse_args with no arguments (US1)
# ---------------------------------------------------------------------------

class TestParseArgsDefaults:
    def test_empty_argv_length_default(self):
        from passgen.cli import parse_args
        ns = parse_args([])
        assert ns.length == 16

    def test_empty_argv_no_symbols_default(self):
        from passgen.cli import parse_args
        ns = parse_args([])
        assert ns.no_symbols is False

    def test_empty_argv_no_numbers_default(self):
        from passgen.cli import parse_args
        ns = parse_args([])
        assert ns.no_numbers is False

    def test_help_exits_zero(self):
        from passgen.cli import parse_args
        with pytest.raises(SystemExit) as exc_info:
            parse_args(["--help"])
        assert exc_info.value.code == 0


# ---------------------------------------------------------------------------
# T014 — parse_args with --length (US2)
# ---------------------------------------------------------------------------

class TestParseArgsLength:
    def test_length_32(self):
        from passgen.cli import parse_args
        ns = parse_args(["--length", "32"])
        assert ns.length == 32

    def test_length_invalid_non_integer_exits_nonzero(self, capsys):
        from passgen.cli import parse_args
        with pytest.raises(SystemExit) as exc_info:
            parse_args(["--length", "abc"])
        assert exc_info.value.code != 0

    def test_main_length_too_short_exits_1(self, capsys):
        from passgen.cli import main
        with pytest.raises(SystemExit) as exc_info:
            main(["--length", "4"])
        captured = capsys.readouterr()
        assert exc_info.value.code == 1
        assert captured.out == ""
        assert "Error: --length must be at least 8" in captured.err

    def test_main_length_too_long_exits_1(self, capsys):
        from passgen.cli import main
        with pytest.raises(SystemExit) as exc_info:
            main(["--length", "129"])
        captured = capsys.readouterr()
        assert exc_info.value.code == 1
        assert captured.out == ""
        assert "Error: --length must be at most 128" in captured.err


# ---------------------------------------------------------------------------
# T018 — parse_args for --no-symbols / --no-numbers flags (US3)
# ---------------------------------------------------------------------------

class TestParseArgsFlags:
    def test_no_symbols_flag(self):
        from passgen.cli import parse_args
        ns = parse_args(["--no-symbols"])
        assert ns.no_symbols is True

    def test_no_numbers_flag(self):
        from passgen.cli import parse_args
        ns = parse_args(["--no-numbers"])
        assert ns.no_numbers is True

    def test_both_flags(self):
        from passgen.cli import parse_args
        ns = parse_args(["--no-symbols", "--no-numbers"])
        assert ns.no_symbols is True
        assert ns.no_numbers is True


# ---------------------------------------------------------------------------
# T022 — stdout/stderr isolation invariants for all exit-code scenarios
# ---------------------------------------------------------------------------

class TestStdoutStderrIsolation:
    """Password value must never appear in stderr for any exit code scenario."""

    def _run_main_capture(self, argv, capsys):
        from passgen.cli import main
        try:
            main(argv)
            exit_code = 0
        except SystemExit as e:
            exit_code = e.code
        return exit_code, capsys.readouterr()

    def test_exit_0_password_not_in_stderr(self, capsys, monkeypatch):
        """Exit 0: password on stdout only, not in stderr."""
        import passgen.cli as cli_mod
        monkeypatch.setattr(cli_mod, "copy_to_clipboard", lambda pw: True)
        exit_code, captured = self._run_main_capture([], capsys)
        assert exit_code == 0
        password = captured.out.strip()
        assert password != ""
        assert password not in captured.err
        assert captured.out == password + "\n"
        assert "Password copied to clipboard." in captured.err

    def test_exit_1_stderr_non_empty(self, capsys):
        """Exit 1: stderr non-empty, stdout empty."""
        exit_code, captured = self._run_main_capture(["--length", "4"], capsys)
        assert exit_code == 1
        assert captured.out == ""
        assert captured.err != ""

    def test_exit_2_password_not_in_stderr(self, capsys, monkeypatch):
        """Exit 2: password on stdout, warning on stderr, password not in stderr."""
        import passgen.cli as cli_mod
        monkeypatch.setattr(cli_mod, "copy_to_clipboard", lambda pw: False)
        exit_code, captured = self._run_main_capture([], capsys)
        assert exit_code == 2
        password = captured.out.strip()
        assert password != ""
        assert password not in captured.err
        assert captured.out == password + "\n"
        assert captured.err != ""

    def test_exit_2_stdout_contains_only_password(self, capsys, monkeypatch):
        """Exit 2: stdout contains exactly password + newline."""
        import passgen.cli as cli_mod
        monkeypatch.setattr(cli_mod, "copy_to_clipboard", lambda pw: False)
        exit_code, captured = self._run_main_capture([], capsys)
        assert exit_code == 2
        assert "\n" in captured.out
        assert captured.out.count("\n") == 1
