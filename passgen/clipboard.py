import pyperclip


def copy_to_clipboard(password: str) -> bool:
    """Copy password to clipboard. Returns True on success, False on failure."""
    try:
        pyperclip.copy(password)
        return True
    except pyperclip.PyperclipException:
        return False
