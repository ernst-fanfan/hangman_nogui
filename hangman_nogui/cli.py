"""Command-line interface for the Hangman game."""

from __future__ import annotations

import argparse
import subprocess
import sys
from functools import lru_cache
from random import choice
from typing import Any, Callable, Sequence

from english_words import get_english_words_set
from rich.align import Align
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text

from .images import get_hangman_image, get_victory_image

#: simple function registry used by the game loop
_FUNCTIONS: dict[str, Callable[[dict[str, Any]], Any]] = {}
console = Console()


def _register_function(name: str):
    def decorator(func: Callable[[dict[str, Any]], Any]):
        func._hangman_name = name  # type: ignore[attr-defined]
        return func

    return decorator


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Play Hangman in your terminal.")
    parser.add_argument(
        "--word",
        help="Play with a specific word (skips dictionary lookup).",
    )
    parser.add_argument(
        "--word-set",
        default="web2",
        help="Dictionary name to draw random words from (default: web2).",
    )
    parser.add_argument(
        "--auto-close-terminal",
        dest="auto_close_terminal",
        action="store_true",
        help="Close the console/terminal window when the game ends.",
    )
    parser.add_argument(
        "--keep-terminal-open",
        dest="auto_close_terminal",
        action="store_false",
        help="Prevent the terminal window from closing automatically on exit.",
    )
    parser.set_defaults(auto_close_terminal=None)
    args = parser.parse_args(argv)
    if args.auto_close_terminal is None:
        args.auto_close_terminal = bool(getattr(sys, "frozen", False))
    return args


@lru_cache(maxsize=None)
def _load_words(word_set: str) -> Sequence[str]:
    return tuple(sorted(get_english_words_set([word_set])))


def build_game(
    *,
    word: str | None = None,
    word_set: str = "web2",
    input_func: Callable[[str], str] = input,
) -> dict[str, Any]:
    dictionary = _load_words(word_set) if word is None else ()
    selected_word = word.lower() if word else choice(dictionary).lower()
    return {
        "is_running": True,
        "word_to_guess": selected_word,
        "guessed_letters": set(),
        "max_attempts": 6,
        "attempts_left": 6,
        "guess": "",
        "input_func": input_func,
        "quit_requested": False,
    }


def build_registry() -> None:
    for name, func in globals().items():
        if callable(func) and hasattr(func, "_hangman_name"):
            hangman_name = getattr(func, "_hangman_name")
            _FUNCTIONS[hangman_name] = func


def run(func: Callable[[dict[str, Any]], Any], game: dict[str, Any]) -> Any:
    return func(game)


@_register_function("display screen")
def display_screen(game: dict[str, Any]) -> None:
    # Clear the screen
    console.clear()

    # Create layout with header, body, footer
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="body"),
        Layout(name="footer", size=5),
    )

    # Header - Game title
    header_text = Text("🎮 HANGMAN GAME", style="bold cyan", justify="center")
    layout["header"].update(Panel(header_text, style="blue"))

    # Body - Split into hangman image and game info
    layout["body"].split_row(
        Layout(name="hangman", ratio=1),
        Layout(name="game_info", ratio=1),
    )

    # Hangman image based on attempts left
    hangman_art = get_hangman_image(game["attempts_left"])
    hangman_style = (
        "red" if game["attempts_left"] <= 2 else "yellow" if game["attempts_left"] <= 4 else "green"
    )
    hangman_text = Text(hangman_art, no_wrap=True)
    layout["hangman"].update(
        Panel(
            Align.center(hangman_text, vertical="middle"),
            title="Hangman",
            style=hangman_style,
            expand=True,
        )
    )

    # Game state info
    word_display = " ".join(
        letter.upper() if letter in game["guessed_letters"] else "_" for letter in game["word_to_guess"]
    )

    game_info_content = Text()
    game_info_content.append(f"Word: {word_display}\n\n", style="bold white")
    game_info_content.append(f"Attempts left: {game['attempts_left']}\n\n", style="yellow")
    game_info_content.append(
        f"Guessed letters:\n{', '.join(sorted(game['guessed_letters'])) if game['guessed_letters'] else 'None'}",
        style="dim",
    )

    layout["game_info"].update(Panel(Align.center(game_info_content), title="Game Status", style="green"))

    # Footer - Instructions
    footer_text = Text("Enter a letter to guess (or 'quit' to exit)", style="italic dim", justify="center")
    layout["footer"].update(Panel(footer_text, style="magenta"))

    # Render the layout
    console.print(layout)


@_register_function("process guess")
def process_guess(game: dict[str, Any]) -> None:
    guess = game["guess"].lower().strip()

    # Handle quit command
    if guess == "quit":
        game["is_running"] = False
        console.print("\n[bold red]Thanks for playing![/bold red]")
        game["quit_requested"] = True
        return

    if len(guess) != 1 or not guess.isalpha():
        console.print("\n[bold red]⚠️  Please enter a single letter.[/bold red]")
        game["input_func"]("Press Enter to continue...")
        return

    if guess in game["guessed_letters"]:
        console.print(f"\n[bold yellow]⚠️  You already guessed '{guess.upper()}'.[/bold yellow]")
        game["input_func"]("Press Enter to continue...")
        return

    game["guessed_letters"].add(guess)

    if guess not in game["word_to_guess"]:
        game["attempts_left"] -= 1
        console.print(f"\n[bold red]❌ Wrong guess! '{guess.upper()}' is not in the word.[/bold red]")
    else:
        console.print(f"\n[bold green]✅ Good guess! '{guess.upper()}' is in the word.[/bold green]")

    # Check win condition
    if all(letter in game["guessed_letters"] for letter in game["word_to_guess"]):
        console.print(
            f"\n[bold green]🎉 Congratulations! You've guessed the word: {game['word_to_guess'].upper()}[/bold green]"
        )
        hangman_text = Text(get_victory_image(), no_wrap=True)
        console.print(Panel(Align.center(hangman_text, vertical="middle"), title="VICTORY!", style="bold green"))
        game["is_running"] = False
    elif game["attempts_left"] <= 0:
        console.print(f"\n[bold red]💀 Game over! The word was: {game['word_to_guess'].upper()}[/bold red]")
        hangman_text = Text(get_hangman_image(-1), no_wrap=True)
        console.print(Panel(Align.center(hangman_text, vertical="middle"), title="GAME OVER", style="bold red"))
        game["is_running"] = False

    if game["is_running"]:
        game["input_func"]("Press Enter to continue...")


def _close_terminal_if_requested(enabled: bool) -> None:
    if not enabled:
        return
    try:
        if sys.platform == "darwin":
            subprocess.run(
                [
                    "osascript",
                    "-e",
                    'tell application "Terminal" to close (every window whose frontmost is true)',
                ],
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        elif sys.platform.startswith("win"):
            import ctypes

            hwnd = ctypes.windll.kernel32.GetConsoleWindow()  # type: ignore[attr-defined]
            if hwnd:
                ctypes.windll.user32.PostMessageW(hwnd, 0x0010, 0, 0)  # type: ignore[attr-defined]
    except Exception:
        pass


def main(argv: Sequence[str] | None = None, *, input_func: Callable[[str], str] = input) -> int:
    args = parse_args(argv)

    build_registry()
    while True:
        game = build_game(word=args.word, word_set=args.word_set, input_func=input_func)
        while game["is_running"]:
            run(_FUNCTIONS["display screen"], game)
            game["guess"] = input_func("Enter your guess: ")
            run(_FUNCTIONS["process guess"], game)

        if game.get("quit_requested") or args.word:
            break

        while True:
            response = input_func("Play again? (y/n): ").strip().lower()
            if response in {"y", "yes"}:
                console.print("\n[bold cyan]Starting a new game![/bold cyan]")
                break
            if response in {"n", "no"}:
                _close_terminal_if_requested(args.auto_close_terminal)
                return 0
            console.print("[bold red]Please answer with 'y' or 'n'.[/bold red]")

    _close_terminal_if_requested(args.auto_close_terminal)
    return 0


if __name__ == "__main__":  # pragma: no cover - script entry point
    main()
