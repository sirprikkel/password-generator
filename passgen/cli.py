import sys
import argparse


from passgen.generator import PasswordConfig, generate_password
from passgen.clipboard import copy_to_clipboard


def parse_args(argv=None):
    """Parse CLI arguments and return namespace with defaults."""
    parser = argparse.ArgumentParser(
        prog="passgen",
        description="Generate a cryptographically secure password.",
    )
    parser.add_argument(
        "--length",
        type=int,
        default=16,
        metavar="N",
        help="Number of characters in the password (8–128, default: 16).",
    )
    parser.add_argument(
        "--no-symbols",
        action="store_true",
        default=False,
        help="Exclude symbol characters from the password.",
    )
    parser.add_argument(
        "--no-numbers",
        action="store_true",
        default=False,
        help="Exclude numeric characters from the password.",
    )
    return parser.parse_args(argv)


def main(argv=None):
    """CLI entry point."""
    args = parse_args(argv)

    # Validate --length bounds
    if args.length < 8:
        sys.stderr.write("Error: --length must be at least 8.\n")
        sys.exit(1)
    if args.length > 128:
        sys.stderr.write("Error: --length must be at most 128.\n")
        sys.exit(1)

    config = PasswordConfig(
        length=args.length,
        include_symbols=not args.no_symbols,
        include_numbers=not args.no_numbers,
    )

    password = generate_password(config)
    sys.stdout.write(password + "\n")

    success = copy_to_clipboard(password)
    if success:
        sys.stderr.write("Password copied to clipboard.\n")
        sys.exit(0)
    else:
        sys.stderr.write(
            "Warning: could not copy to clipboard — paste from terminal output.\n"
        )
        sys.exit(2)


if __name__ == "__main__":
    main()
