# Row-Column Game (RC-Game)

A modular, console-based strategy game developed in Python as a six-member group project for the **Advanced Python Programming for Economics, Management and Finance** course at Bocconi University.

Players alternate selecting numbered cells from a grid, with each move constrained by the row or column of the previous move. The objective is to finish the game with the highest total score.

## Features

- Human vs Human, Human vs Computer, and Computer vs Computer modes
- Configurable board size, starting player, random seed, and preset boards
- Four computer-player strategies with different decision rules
- Modular separation of game logic, board management, strategies, and scorekeeping
- CSV-based persistent match history
- Cross-platform terminal interface
- No third-party dependencies

## Computer Strategies

The game includes four pluggable strategies:

- **Greedy** - chooses the highest-value legal move available immediately.
- **MaximizeFutureMin** - evaluates the next turn and balances the current gain against the opponent's possible response.
- **MinimizeOpponentOptions** - attempts to leave the opponent with the smallest number of legal follow-up moves.
- **PreserveHighValues** - uses a defensive approach designed to avoid exposing high-value cells to the opponent.

## Project Structure

```text
row-column-game/
├── main.py              # Application entry point, menus and configuration
├── game_engine.py       # Core game loop, turn logic and state management
├── board_manager.py     # Board generation, rendering and move validation
├── strategies.py        # Computer-player strategies
├── scorekeeper.py       # CSV-based match history
├── config.txt           # Default game configuration
├── requirements.txt     # Python requirements information
└── docs/
    ├── ARCHITECTURE_GUIDE.md
    ├── USER_MANUAL.md
    └── AUTHORS.txt
```

## My Contribution

My main contributions to the project focused on the technical core of the application:

- Developed and refined parts of the **core game logic**.
- Contributed to the implementation of **computer-player strategies** and their decision-making logic.
- Took a key role in **integrating code produced by different team members** into the final working application and ensuring consistency across modules.

The complete project was developed collaboratively by a six-member team. All contributors are listed in [`docs/AUTHORS.txt`](docs/AUTHORS.txt).

## Requirements

- Python 3.7 or later
- No external packages are required; the project uses only the Python standard library.

## How to Run

Clone the repository and move into the project directory:

```bash
git clone https://github.com/fabriziogorelli99-ops/Row-Column-Game.git
cd row-column-game
```

Run the game with:

```bash
python main.py
```

Depending on your system, you may need to use:

```bash
python3 main.py
```

## Gameplay

At launch, the main menu allows you to start a game, adjust the configuration, view match history, or exit. During a match, players select a numbered cell from the board. After the first move, the next legal move must be in the same row or column as the previous selection.

The value of each selected cell is added to that player's score. The match ends when no legal moves remain, and the player with the highest score wins.

For full instructions, see the [`User Manual`](docs/USER_MANUAL.md).

## Technical Design

The project is divided into independent modules so that gameplay rules, user interaction, computer strategies, and persistence can be modified separately. The computer-player strategies interact with the board through a common interface, making it possible to add new strategies without redesigning the rest of the application.

For a more detailed explanation, see the [`Architecture Guide`](docs/ARCHITECTURE_GUIDE.md).

## Authors

Developed as a group project at Bocconi University. See [`docs/AUTHORS.txt`](docs/AUTHORS.txt) for the full contributor list.
