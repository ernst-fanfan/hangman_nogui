from typing import Any
from english_words import get_english_words_set
from random import choice
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from images import get_hangman_image, get_victory_image

_: dict[str, Any] = {}
console = Console()

def _register_function(name: str):
    def decorator(func):
        func._hangman_name = name
        return func
    return decorator

def build_game() -> dict[str, Any]:
    
    return {
        "is_running": True,
        "word_to_guess": choice(list(get_english_words_set(['web2']))).lower(),
        "guessed_letters": set(),
        "max_attempts": 6,
        "attempts_left": 6,
        "guess": "",
    }
    
def build_registry():
    for name, func in globals().items():
        if callable(func) and hasattr(func, "_hangman_name"):
            hangman_name = getattr(func, "_hangman_name")
            _[hangman_name] = func

def run(func, game: dict[str, Any]) -> Any:
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
        Layout(name="footer", size=5)
    )
    
    # Header - Game title
    header_text = Text("🎮 HANGMAN GAME", style="bold cyan", justify="center")
    layout["header"].update(Panel(header_text, style="blue"))
    
    # Body - Split into hangman image and game info
    layout["body"].split_row(
        Layout(name="hangman", ratio=1),
        Layout(name="game_info", ratio=1)
    )
    
    # Hangman image based on attempts left
    hangman_art = get_hangman_image(game["attempts_left"])
    hangman_style = "red" if game["attempts_left"] <= 2 else "yellow" if game["attempts_left"] <= 4 else "green"
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
    word_display = ' '.join(
        letter.upper() if letter in game["guessed_letters"] else '_' 
        for letter in game["word_to_guess"]
    )
    
    game_info_content = Text()
    game_info_content.append(f"Word: {word_display}\n\n", style="bold white")
    game_info_content.append(f"Attempts left: {game['attempts_left']}\n\n", style="yellow")
    game_info_content.append(f"Guessed letters:\n{', '.join(sorted(game['guessed_letters'])) if game['guessed_letters'] else 'None'}", style="dim")
    
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
    if guess == 'quit':
        game["is_running"] = False
        console.print("\n[bold red]Thanks for playing![/bold red]")
        return
    
    if len(guess) != 1 or not guess.isalpha():
        console.print("\n[bold red]⚠️  Please enter a single letter.[/bold red]")
        input("Press Enter to continue...")
        return
    
    if guess in game["guessed_letters"]:
        console.print(f"\n[bold yellow]⚠️  You already guessed '{guess.upper()}'.[/bold yellow]")
        input("Press Enter to continue...")
        return
    
    game["guessed_letters"].add(guess)
    
    if guess not in game["word_to_guess"]:
        game["attempts_left"] -= 1
        console.print(f"\n[bold red]❌ Wrong guess! '{guess.upper()}' is not in the word.[/bold red]")
    else:
        console.print(f"\n[bold green]✅ Good guess! '{guess.upper()}' is in the word.[/bold green]")
    
    # Check win condition
    if all(letter in game["guessed_letters"] for letter in game["word_to_guess"]):
        console.print(f"\n[bold green]🎉 Congratulations! You've guessed the word: {game['word_to_guess'].upper()}[/bold green]")
        hangman_art = get_victory_image()
        hangman_text = Text(hangman_art, no_wrap=True)
        console.print(Panel(Align.center(hangman_text, vertical="middle"), title="VICTORY!", style="bold green"))
        game["is_running"] = False
    elif game["attempts_left"] <= 0:
        console.print(f"\n[bold red]💀 Game over! The word was: {game['word_to_guess'].upper()}[/bold red]")
        hangman_art = get_hangman_image(-1)
        hangman_text = Text(hangman_art, no_wrap=True)
        console.print(Panel(Align.center(hangman_text, vertical="middle"), title="GAME OVER", style="bold red"))
        game["is_running"] = False
    
    if game["is_running"]:
        input("Press Enter to continue...")

def main() -> None:
    build_registry()
    game = build_game()
    while game["is_running"]:
        run(_["display screen"], game)
        game["guess"] = input("Enter your guess: ")
        run(_["process guess"], game)


if __name__ == "__main__":
    main()
