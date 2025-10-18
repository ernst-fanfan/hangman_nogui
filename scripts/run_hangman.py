"""Shim script for PyInstaller builds."""

from hangman_nogui.cli import main


if __name__ == "__main__":
    raise SystemExit(main())
