import secrets
from dataclasses import dataclass


class CharacterSet:
    LOWERCASE = "abcdefghijklmnopqrstuvwxyz"
    UPPERCASE = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    NUMBERS = "0123456789"
    SYMBOLS = "!@#$%^&*()-_=+[]{}|;:,.<>?"


@dataclass
class PasswordConfig:
    length: int = 16
    include_symbols: bool = True
    include_numbers: bool = True


def secure_shuffle(lst: list) -> None:
    """Fisher-Yates in-place shuffle using secrets.randbelow (CSPRNG)."""
    for i in range(len(lst) - 1, 0, -1):
        j = secrets.randbelow(i + 1)
        lst[i], lst[j] = lst[j], lst[i]


def generate_password(config: PasswordConfig) -> str:
    """Generate a cryptographically secure password per the given config."""
    # 1. Mandatory pool (always included)
    pool = CharacterSet.LOWERCASE + CharacterSet.UPPERCASE

    # 2. Guarantee at least one character from each enabled set
    guaranteed = [
        secrets.choice(CharacterSet.LOWERCASE),
        secrets.choice(CharacterSet.UPPERCASE),
    ]

    if config.include_numbers:
        guaranteed.append(secrets.choice(CharacterSet.NUMBERS))
        pool += CharacterSet.NUMBERS

    if config.include_symbols:
        guaranteed.append(secrets.choice(CharacterSet.SYMBOLS))
        pool += CharacterSet.SYMBOLS

    # 3. Fill remaining positions from combined pool
    remaining = config.length - len(guaranteed)
    filler = [secrets.choice(pool) for _ in range(remaining)]

    # 4. Cryptographically secure shuffle
    chars = guaranteed + filler
    secure_shuffle(chars)

    return "".join(chars)
