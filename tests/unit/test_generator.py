"""Unit tests for passgen.generator — TDD: tests written before implementation."""


# ---------------------------------------------------------------------------
# T004 — CharacterSet constants and PasswordConfig dataclass
# ---------------------------------------------------------------------------

class TestCharacterSetConstants:
    def test_lowercase_characters(self):
        from passgen.generator import CharacterSet
        assert CharacterSet.LOWERCASE == "abcdefghijklmnopqrstuvwxyz"

    def test_uppercase_characters(self):
        from passgen.generator import CharacterSet
        assert CharacterSet.UPPERCASE == "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    def test_numbers_characters(self):
        from passgen.generator import CharacterSet
        assert CharacterSet.NUMBERS == "0123456789"

    def test_symbols_characters(self):
        from passgen.generator import CharacterSet
        assert CharacterSet.SYMBOLS == "!@#$%^&*()-_=+[]{}|;:,.<>?"

    def test_no_overlap_lowercase_uppercase(self):
        from passgen.generator import CharacterSet
        assert set(CharacterSet.LOWERCASE) & set(CharacterSet.UPPERCASE) == set()

    def test_no_overlap_lowercase_numbers(self):
        from passgen.generator import CharacterSet
        assert set(CharacterSet.LOWERCASE) & set(CharacterSet.NUMBERS) == set()

    def test_no_overlap_lowercase_symbols(self):
        from passgen.generator import CharacterSet
        assert set(CharacterSet.LOWERCASE) & set(CharacterSet.SYMBOLS) == set()

    def test_no_overlap_uppercase_numbers(self):
        from passgen.generator import CharacterSet
        assert set(CharacterSet.UPPERCASE) & set(CharacterSet.NUMBERS) == set()

    def test_no_overlap_uppercase_symbols(self):
        from passgen.generator import CharacterSet
        assert set(CharacterSet.UPPERCASE) & set(CharacterSet.SYMBOLS) == set()

    def test_no_overlap_numbers_symbols(self):
        from passgen.generator import CharacterSet
        assert set(CharacterSet.NUMBERS) & set(CharacterSet.SYMBOLS) == set()


class TestPasswordConfig:
    def test_default_length(self):
        from passgen.generator import PasswordConfig
        config = PasswordConfig()
        assert config.length == 16

    def test_default_include_symbols(self):
        from passgen.generator import PasswordConfig
        config = PasswordConfig()
        assert config.include_symbols is True

    def test_default_include_numbers(self):
        from passgen.generator import PasswordConfig
        config = PasswordConfig()
        assert config.include_numbers is True

    def test_custom_length(self):
        from passgen.generator import PasswordConfig
        config = PasswordConfig(length=32)
        assert config.length == 32

    def test_custom_flags(self):
        from passgen.generator import PasswordConfig
        config = PasswordConfig(include_symbols=False, include_numbers=False)
        assert config.include_symbols is False
        assert config.include_numbers is False


# ---------------------------------------------------------------------------
# T008 — generate_password with default config
# ---------------------------------------------------------------------------

class TestGeneratePasswordDefault:
    def test_length_is_16_by_default(self):
        from passgen.generator import PasswordConfig, generate_password
        result = generate_password(PasswordConfig())
        assert len(result) == 16

    def test_all_chars_in_full_alphabet(self):
        from passgen.generator import CharacterSet, PasswordConfig, generate_password
        full_alphabet = (
            CharacterSet.LOWERCASE + CharacterSet.UPPERCASE
            + CharacterSet.NUMBERS + CharacterSet.SYMBOLS
        )
        result = generate_password(PasswordConfig())
        for ch in result:
            assert ch in full_alphabet

    def test_at_least_one_from_each_enabled_set_100_runs(self):
        from passgen.generator import CharacterSet, PasswordConfig, generate_password
        for _ in range(100):
            result = generate_password(PasswordConfig())
            assert any(ch in CharacterSet.LOWERCASE for ch in result)
            assert any(ch in CharacterSet.UPPERCASE for ch in result)
            assert any(ch in CharacterSet.NUMBERS for ch in result)
            assert any(ch in CharacterSet.SYMBOLS for ch in result)

    def test_two_successive_calls_differ(self):
        from passgen.generator import PasswordConfig, generate_password
        assert generate_password(PasswordConfig()) != generate_password(PasswordConfig())


# ---------------------------------------------------------------------------
# T017 — generate_password with non-default configs (US3)
# ---------------------------------------------------------------------------

class TestGeneratePasswordConfigs:
    def test_no_symbols_excludes_symbol_chars(self):
        from passgen.generator import CharacterSet, PasswordConfig, generate_password
        config = PasswordConfig(length=32, include_symbols=False)
        for _ in range(20):
            result = generate_password(config)
            for ch in result:
                assert ch not in CharacterSet.SYMBOLS

    def test_no_numbers_excludes_digit_chars(self):
        from passgen.generator import CharacterSet, PasswordConfig, generate_password
        config = PasswordConfig(length=32, include_numbers=False)
        for _ in range(20):
            result = generate_password(config)
            for ch in result:
                assert ch not in CharacterSet.NUMBERS

    def test_letters_only_excludes_numbers_and_symbols(self):
        from passgen.generator import CharacterSet, PasswordConfig, generate_password
        config = PasswordConfig(length=32, include_symbols=False, include_numbers=False)
        for _ in range(20):
            result = generate_password(config)
            for ch in result:
                assert ch in (CharacterSet.LOWERCASE + CharacterSet.UPPERCASE)

    def test_no_symbols_correct_length(self):
        from passgen.generator import PasswordConfig, generate_password
        config = PasswordConfig(length=24, include_symbols=False)
        assert len(generate_password(config)) == 24

    def test_no_numbers_correct_length(self):
        from passgen.generator import PasswordConfig, generate_password
        config = PasswordConfig(length=24, include_numbers=False)
        assert len(generate_password(config)) == 24

    def test_letters_only_correct_length(self):
        from passgen.generator import PasswordConfig, generate_password
        config = PasswordConfig(length=24, include_symbols=False, include_numbers=False)
        assert len(generate_password(config)) == 24

    def test_at_least_one_lowercase_always(self):
        from passgen.generator import CharacterSet, PasswordConfig, generate_password
        configs = [
            PasswordConfig(include_symbols=False),
            PasswordConfig(include_numbers=False),
            PasswordConfig(include_symbols=False, include_numbers=False),
        ]
        for config in configs:
            for _ in range(20):
                result = generate_password(config)
                assert any(ch in CharacterSet.LOWERCASE for ch in result)

    def test_at_least_one_uppercase_always(self):
        from passgen.generator import CharacterSet, PasswordConfig, generate_password
        configs = [
            PasswordConfig(include_symbols=False),
            PasswordConfig(include_numbers=False),
            PasswordConfig(include_symbols=False, include_numbers=False),
        ]
        for config in configs:
            for _ in range(20):
                result = generate_password(config)
                assert any(ch in CharacterSet.UPPERCASE for ch in result)


# ---------------------------------------------------------------------------
# T021 — CSPRNG static verification (no 'import random' in generator.py)
# ---------------------------------------------------------------------------

class TestCsprngStaticVerification:
    def test_secrets_imported_in_generator(self):
        import pathlib
        src = pathlib.Path(__file__).parent.parent.parent / "passgen" / "generator.py"
        text = src.read_text()
        assert "import secrets" in text

    def test_random_not_imported_in_generator(self):
        import pathlib
        src = pathlib.Path(__file__).parent.parent.parent / "passgen" / "generator.py"
        text = src.read_text()
        assert "import random" not in text
