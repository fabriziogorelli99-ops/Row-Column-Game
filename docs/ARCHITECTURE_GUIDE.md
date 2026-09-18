# Row-Column Game (RC-Game) — Architecture and Technical Guide

## Table of Contents

1.  Overview
2.  System Architecture
3.  Data Flow
4.  Module Documentation
5.  Data Structures
6.  Design Principles
7.  Conclusion

---

## 1. Overview

The **Row-Column Game (RC-Game)** is a modular, console-based Python project developed as a demonstration of structured design, clean code, and algorithmic strategy. It serves as both an educational tool and a framework for exploring decision-making systems. The game involves two players—either human or computer to claim the highest total score by alternately selecting numbered cells from a shared grid. After each move, the next player is constrained to select only from the same row or column as the previous move.

The project emphasizes modular construction and loose coupling between its components. Its design draws inspiration from classical turn-based strategy games, but it operates entirely through the command line for maximum portability and clarity. Each module is written to be self-explanatory, following best practices in readability and separation of concerns.

**Key Characteristics**

-   Pure Python 3.7+ implementation (no third-party dependencies).
-   Multiple play modes: Human vs Human, Human vs Computer, and Computer vs Computer.
-   4x Pluggable computer strategies.
-   Cross-platform compatibility across Windows, macOS, and Linux.
-   Persistent configuration and game history tracking.

By focusing on readability, reusability, and clean modular interactions, the RC-Game offers an elegant case study in designing small yet scalable software architectures.

---

## 2. System Architecture

### Architectural Overview

The RC-Game is composed of several interconnected but independent modules. Each one serves a well-defined role, and their interactions are handled through lightweight data transfer objects and standardized function interfaces. This creates an environment where developers can focus on one part of the system without risking regressions in others.

```
┌──────────────────────────────────────────┐│               main.py                    ││  • Menu and Config Management            ││  • Application Entry Point               │└──────────────────┬───────────────────────┘                   │                   ▼┌──────────────────────────────────────────┐│             game_engine.py               ││  • Core Game Loop and Turn Logic         ││  • Input Handling and State Management   ││  • Score Calculation and Game End Logic  │└───────────────┬───────────────┬──────────┘                │               │       ┌────────▼──────┐   ┌────▼──────────┐       │ board_manager │   │  strategies   │       │ • Grid Rules  │   │ • Behaviors   │       │ • Display     │   └───────────────┘       └───────────────┘                   │                ▼┌──────────────────────────────────────────┐│            scorekeeper.py                ││ • Persistent Match History               ││ • CSV-Based Result Tracking              │└──────────────────────────────────────────┘
```

The modular nature ensures that a change in, for instance, the computer logic does not affect how the board is rendered or how user input is parsed. This independence of layers leads to high maintainability and makes it easy to integrate new strategies or tweak the UI behavior.

---

## 3. Data Flow

The RC-Game follows a clean, cyclical flow pattern typical of interactive terminal games. The lifecycle of a game session begins from the configuration stage, flows into the main game loop, and ends with persistence of results. Each stage is designed for clarity and user control.

### Startup Sequence

```
1. User runs python main.py2. The system reads configuration from config.txt3. A menu interface is presented4. The player selects “Play”5. The configuration object (GameConfig) is instantiated6. The game engine is initialized and BoardManager is prepared7. Gameplay begins
```

This structured startup ensures deterministic initialization and reproducibility, especially when a random seed is specified. Even the random-number generator within the board is seeded through configuration, ensuring that identical setups yield identical game boards across sessions.

### Gameplay Loop

Gameplay proceeds through alternating turns between Player A and Player B. Each round adheres to a fixed rhythm of input, validation, scoring, and display refresh. The `game_engine` manages every cycle, checking valid positions via the board manager and invoking either human input prompts or computer strategy evaluations depending on the current player type.

This turn-based flow keeps state transitions simple and visible. Since the board and all calculations are explicitly re-rendered each round, debugging or tracing the match flow becomes straightforward—an intentional design choice to make the system both transparent and testable.

---

## 4. Module Documentation

### 4.1 main.py — User Interface and Application Control

**Purpose:**  
Acts as the primary coordinator of all user-facing interactions. It manages menus, configuration adjustment, and high-level transitions between modes.

**Responsibilities**

-   Provides main menu options (“Play”, “Adjust Config”, “History”, “Exit”).
-   Handles loading and saving configuration files.
-   Facilitates new game sessions and post-game review options.
-   Manages history viewing and user prompts.

Beyond simple input handling, `main.py` structures the program’s interaction model. It acts as the gateway through which all user commands are interpreted and routed to the correct module. This ensures that the system maintains a consistent interface layer, keeping the game engine entirely free of I/O logic.

**Highlights**

-   Graceful input handling (`Menu`, `Back`, and `Exit` commands).
-   Interactive configuration editing with validation checks.
-   Post-game menu for replay and saving results.

---

### 4.2 game_engine.py — Core Game Logic

**Purpose:**  
Implements the logical core of the RC-Game. It defines how the board evolves, how turns alternate, and how victory is determined. This is the brain of the system, connecting high-level configuration with low-level gameplay.

**Behavioral Overview**

1.  Initializes the `BoardManager` based on the configuration parameters.
2.  Assigns player controllers based on the selected mode (human or computer).
3.  Runs a loop until no legal moves remain.
4.  Executes validation for all moves before committing them.
5.  Records and displays round-by-round progress.

The engine includes clear textual output showing every move made, the corresponding board state, and the running score totals. Such verbosity is deliberate—it aids transparency and debugging, while also helping beginners trace logic flow visually.

**Output Example**

```python
{  "a_score": 34,  "b_score": 27,  "rounds": 16,  "mode": "H_VS_C",  "winner": "A"}
```

The clarity of this data-driven return format allows external tools or scripts to analyze outcomes without needing to parse console output manually.

---

### 4.3 board_manager.py — Grid and Rule Management

**Purpose:**  
Manages all data and logic associated with the game grid. This module is effectively the “world” of the game—responsible for defining where moves can occur and what effects they produce.

**Key Functions**

-   **Initialization:** Creates either a random or user-specified preset grid.
-   **Validation:** Ensures moves are within bounds and on available cells.
-   **Rule Enforcement:** Restricts next moves to the same row or column.
-   **Rendering:** Generates an ASCII-art visualization of the board’s current state.

The `BoardManager` also contains helper methods such as `max_remaining_value()`, which allows computer strategies to make informed decisions by examining the board’s remaining high-value cells. This tight integration of data and logic allows strategies to focus purely on reasoning, leaving structural consistency to the manager.

**Display Behavior**  
The grid printout includes headers, coordinates, and a boxed layout with clear delineation of rows and columns. The most recent move is marked with an `X`, emphasizing the game’s evolving structure visually.

---

### 4.4 strategies.py — Artificial Intelligence System

**Purpose:**  
Provides a registry of computer behaviors that can compete autonomously or against humans. Each strategy is a self-contained function that receives a `BoardManager` instance and the last move position, then returns an optimal next move.

**Built-in Strategies**

Name

Description

**Greedy**

Selects the highest-value cell without foresight.

**MaximizeFutureMin**

Looks one move ahead, maximizing its score while minimizing the opponent’s next potential gain.

**MinimizeOpponentOptions**

Chooses the move that leaves the opponent the fewest possible follow-up moves.

**PreserveHighValues**

Avoids exposing globally high-value cells to the opponent, focusing on board preservation.

Each strategy employs small, readable algorithms that simulate moves in-memory, temporarily altering board state before evaluation. Because each function interacts only through the `BoardManager` interface, the computer layer remains decoupled from the rest of the system, enabling easy experimentation with new algorithms.

---

### 4.5 scorekeeper.py — History and Game Records

**Purpose:**  
Responsible for logging and retrieving game outcomes. Results are stored in a CSV format to enable long-term tracking, external analysis, or leaderboard creation.

Each recorded entry includes timestamps, player names, scores, round counts, and game mode. The file is automatically created on first use, ensuring seamless persistence with no setup required.

**Example CSV Entry**

```
2025-11-15 20:43, Alice VS Bob, 28, 33, B, 14, C_VS_C
```

This component helps maintain a tangible record of progress, fostering replayability and competition. It also demonstrates practical file I/O and serialization techniques using only Python’s standard library.

---

### 4.6 config.txt — Persistent Configuration

The configuration file acts as the control hub for the application’s default parameters. Each setting corresponds to a parameter within the `GameConfig` data structure, making the system flexible and user-friendly.

**Example**

```
SIZE=5MODE=H_VS_CSTART_PLAYER=ABOARD_SOURCE=RANDOMA_STRATEGY=GreedyB_STRATEGY=MaximizeFutureMin
```

By externalizing defaults, the program ensures that users or automated systems can tailor experiences without modifying source code. This approach reinforces configurability as a first-class concept in the project’s design philosophy.

---

## 5. Data Structures

The RC-Game relies on a small but expressive set of data abstractions that make the code easy to reason about and extend.

### Position

`Tuple[int, int]` — Represents a cell’s coordinates as (row, column), zero-indexed for internal use.

### Board

`List[List[Optional[int]]]` — A grid containing numeric cell values. Removed or unavailable cells are represented as `None`, making board mutation clear and traceable.

### GameConfig

```python
class GameConfig:    size: int    mode: str    a_strategy: Optional[str]    b_strategy: Optional[str]    seed: Optional[int]    preset_board: Optional[List[int]]    start_player: str
```

This class encapsulates all essential parameters for launching a game. It also serves as the connective tissue between `main.py` and `game_engine.py`, allowing the user interface to define settings declaratively.

### Player Controller

`Tuple[str, Optional[Callable]]` — Defines whether a player is `"human"` or `"computer"`, and, if applicable, references a strategy function used for move generation.

---

## 6. Design Principles

The RC-Game adheres to a philosophy grounded in clarity, composability, and long-term maintainability. Its design encourages experimentation, learning, and structured problem-solving.

### Core Principles

**1. Single Responsibility**  
Each module serves exactly one role. `board_manager.py` manages data and rules, `game_engine.py` manages flow, and `main.py` mediates user interaction.

**2. Loose Coupling and Strong Cohesion**  
Modules communicate through simple data structures rather than complex shared state. This minimizes side effects and promotes reusability.

**3. Transparency and Traceability**  
Every operation, from move selection to score updates, is echoed to the console. This makes the system ideal for educational and debugging purposes.

**4. Determinism Through Seeding**  
By allowing an optional seed parameter, the game ensures repeatable outcomes. This is invaluable for strategy testing or controlled experiments.

**5. Extensibility Through Composition**  
New behaviors can be introduced without altering existing code. Computer strategies, for example, plug into the system through a registry mechanism.

In essence, RC-Game is a model of clarity over complexity. It demonstrates how thoughtful architecture can make even a small console game feel polished and technically robust.

---

## 7. Conclusion

The **Row-Column Game** exemplifies clean modular architecture in Python. Despite its minimal footprint, it integrates essential software engineering concepts—configuration management, state control, reproducibility, and decoupled design. Its architecture makes it an excellent base for experimenting with new computer strategies, visual enhancements, or game mechanics.

Beyond entertainment, the project is a teaching tool. It highlights how even a simple game can be an exercise in thoughtful system design, offering developers a chance to practice maintainability, abstraction, and algorithmic reasoning in a tangible and rewarding format.