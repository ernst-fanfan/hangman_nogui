"""
ASCII Hangman Images for different game states.
Each image corresponds to the number of wrong guesses (6 total attempts).
"""

from __future__ import annotations

import inspect
import textwrap


def _format_art(block: str) -> str:
    """Normalize indentation so ASCII art renders consistently."""
    return textwrap.indent(inspect.cleandoc(block), "   ")


# Hangman stages from 0 wrong guesses to 6 wrong guesses (game over)
HANGMAN_IMAGES = {
    6: _format_art("""
   ┌─────┐
   │
   │
   │
   │
   │
───┴───
"""),
    5: _format_art("""
   ┌─────┐
   │     │
   │
   │
   │
   │
───┴───
"""),
    4: _format_art("""
   ┌─────┐
   │     │
   │     O
   │
   │
   │
───┴───
"""),
    3: _format_art("""
   ┌─────┐
   │     │
   │     O
   │     │
   │
   │
───┴───
"""),
    2: _format_art("""
   ┌─────┐
   │     │
   │     O
   │    /│
   │
   │
───┴───
"""),
    1: _format_art("""
   ┌─────┐
   │     │
   │     O
   │    /│\\
   │
   │
───┴───
"""),
    0: _format_art("""
   ┌─────┐
   │     │
   │     O
   │    /│\\
   │    /
   │
───┴───
"""),
    -1: _format_art("""
   ┌─────┐
   │     │
   │     X
   │    /│\\
   │    / \\
   │
───┴─── 
GAME OVER!
"""),
}


def get_hangman_image(attempts_left: int) -> str:
    """
    Get the hangman ASCII art based on attempts remaining.

    Args:
        attempts_left: Number of attempts remaining (0-6)

    Returns:
        ASCII art string for current hangman state
    """
    if attempts_left < 0:
        return HANGMAN_IMAGES[-1]
    return HANGMAN_IMAGES.get(attempts_left, HANGMAN_IMAGES[0])


def get_victory_image() -> str:
    """
    Get a celebratory ASCII art for winning the game.

    Returns:
        Victory ASCII art string
    """
    return _format_art("""
🎉 VICTORY! 🎉

   ┌─────┐
   │
   │   \\o/
   │    │
   │   / \\
   │
───┴───

You saved the day!
""")
