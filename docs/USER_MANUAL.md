
# Row-Column Game (RC-Game) — User Manual

## Table of Contents
1. Introduction
2. Installation and Setup
3. Game Overview
4. Rules of Play
5. Game Interface and Menus
6. Configuration Settings
7. Game Modes
8. Computer Strategies
9. Playing the Game
10. Global Commands
11. Tips and Strategy Advice
12. Troubleshooting
13. Advanced Configuration
14. Conclusion

---

## 1. Introduction

The **Row-Column Game (RC-Game)** is a two-player, turn-based strategy game played entirely in the terminal. Players alternate selecting numbers from a square grid. Each chosen number is added to the player’s total score. After the opening move, every move must follow a single rule: you may only select a cell in the **same row or column** as your opponent’s previous move.

The game supports **Human vs Human**, **Human vs Computer**, and **Computer vs Computer** modes. The computer players can use various **strategies** ranging from simple greedy selection to look-ahead tactics.

The objective is simple: **finish with the highest score** once no legal moves remain.

---

## 2. Installation and Setup

### Requirements
- **Python 3.7+**
- No external libraries required (uses only Python’s standard library).
- Works on Windows, macOS, and Linux terminals.

### Installation Steps
1. Download or clone the RC-Game project folder.
2. Ensure the following files are in the same directory:

```
main.py
game_engine.py
board_manager.py
strategies.py
scorekeeper.py
config.txt
```

3. Open a terminal in this directory and run:

```bash
python main.py
# or
python3 main.py
```

4. The main menu will appear in the console.

---

## 3. Game Overview

Each play session consists of several **rounds**. Players alternate choosing numbers from a grid.  
Each number can be used only once — once selected, it disappears from the board.

The board size, mode (Human vs Computer, etc.), and strategies are defined by `config.txt` or adjusted through the **Config Menu**.

The program tracks scores, displays the current round, and ends automatically when no valid moves remain.

---

## 4. Rules of Play

1. **Board Creation**:  
   A square grid (e.g., 5×5) filled with random integers between **1 and 9**.  
   Optionally, you can define your own fixed board in `config.txt`.

2. **Opening Move (Round 0)**:  
   - If Player A is **human**, they may choose **any** cell.  
   - If Player A is **computer-controlled**, its selected strategy automatically picks a move from all available cells.

3. **Subsequent Rounds**:  
   From the second move onward, each player must pick a number that lies **in the same row or the same column** as the opponent’s previous move.

4. **Scoring**:  
   The value of the chosen cell is added to the current player’s total score.

5. **Game End**:  
   When no valid moves remain, the final scores are compared.  
   - Highest score → Winner.  
   - Equal scores → Tie.

6. **Display Rule**:  
   - Removed cells are blank, except for the **most recent** move, shown as `'X'`.

---

## 5. Game Interface and Menus

Upon running `main.py`, the following main menu is displayed:

```
==================================================
             Row-Column Game (RC-Game)
==================================================
1. Play
2. Adjust Config
3. Exit
==================================================
Enter choice (1-3):
```

### Menu Options
- **1. Play** — Start a game with the current configuration.
- **2. Adjust Config** — Modify game settings interactively.
- **3. Exit** — Quit the program.

The game screen displays the round number, scores, and a stylized boxed board showing remaining numbers.

---

## 6. Configuration Settings

The configuration determines how the game is played. You can modify it interactively through the Config Menu or manually via `config.txt`.

### Configurable Fields

| Field | Type | Required | Description |
|--------|------|-----------|-------------|
| `SIZE` | Integer | Yes | Size of the board (N×N). Must be ≥ 2. |
| `MODE` | String | Yes | Game mode: `H_VS_H`, `H_VS_C`, or `C_VS_C`. |
| `A_STRATEGY` | String | Conditional | Strategy name if Player A is computer-controlled. |
| `B_STRATEGY` | String | Conditional | Strategy name if Player B is computer-controlled. |
| `SEED` | Integer | No | Random seed for reproducible board generation. |
| `BOARD` | List of Ints | No | Preset list of values (must be exactly SIZE² integers). |

### Example Configuration

```txt
SIZE=5
MODE=H_VS_C
A_STRATEGY=Greedy
B_STRATEGY=MaximizeFutureMin
SEED=42
# Optional preset board (25 values for SIZE=5)
# BOARD=1,2,3,4,5,6,7,8,9,1,2,3,4,5,6,7,8,9,1,2,3,4,5,6
```

---

## 7. Game Modes

1. **H_VS_H** — Human vs Human. Both players input moves manually.
2. **H_VS_C** — Human (A) vs Computer (B). Player B uses the configured strategy.
3. **C_VS_C** — Computer vs Computer. Both A and B play automatically.

---

## 8. Computer Strategies

Each computer player uses a **strategy function** that evaluates the current board and chooses a move.

| Strategy | Description |
|-----------|-------------|
| **Greedy** | Chooses the available move with the highest immediate value. |
| **MaximizeFutureMin** | Looks one move ahead: maximizes `(my value − opponent’s minimal next value)`. |
| **MinimizeOpponentOptions** | Chooses the move that minimizes the opponent’s future options (ties broken by current value). |
| **PreserveHighValues** | Defensive play: avoids giving the opponent access to the board’s highest number. |

---

## 9. Playing the Game

### Gameplay Flow

```
1. Display board and scores
2. Current player selects move
3. Validate move (row/column rule)
4. Update board and scores
5. Switch player
6. Repeat until no moves remain
7. Display final scores and winner
```

### Board Display Example

```
Round 3 (5x5)
┌───────────────┐
│ 1  3  5  2  9 │
│ 4  7  X  1  6 │
│ 5  2     8  4 │
│ 3  9  6  7  1 │
│ 8  4  5  9  2 │
└───────────────┘
Score A: 23 | Score B: 18
```

### Input Format

When prompted:
```
Enter move as Row,Col (1-indexed):
```
Example: `2,3` → row 2, column 3.

Invalid input (out of bounds, empty cell, or not same row/column) will display an error and prompt again.

---

## 10. Global Commands

At any prompt, you can use these special commands:
- **Menu** — Return to Main Menu immediately.
- **Back** — Go up one level (Config Menu only).
- **Exit** — Quit the program instantly.

*Note: Back command is unavailable within a live game*

---

## 11. Tips and Strategy Advice

Focus on control and constraints. Since the rule severely restricts subsequent moves, your primary goal shouldn't just be maximizing your immediate score, but also minimizing your opponent's options and removing high-value cells from their accessible rows and columns. A low-value move that forces your opponent into a dead-end or limits them to only low-scoring rows/columns is often strategically superior to a high-value move that opens up a bounty of points for them on their next turn. Always look at the intersection of the available rows and columns and try to eliminate the most dangerous choices for the opponent.

- **Balance greed and control** — Sometimes restricting your opponent matters more than grabbing a big number.
- **Watch for traps** — Avoid leaving high-value numbers accessible in the same row or column.
- **Seeds are useful** — Set a seed to replay the same board for practice.
- **Observe AIs** — In C_VS_C mode, watch how different strategies behave and learn from them.

---

## 12. Troubleshooting

| Issue | Possible Cause | Solution |
|--------|----------------|-----------|
| “Config file not found” | Missing `config.txt` | Create one manually or rerun setup. |
| “Unknown strategy” | Typo or case mismatch | Check strategy names (`Greedy`, etc.). |
| “Invalid move” | Out of bounds or invalid rule | Enter valid coordinates per row/col constraint. |
| Terminal display issues | Terminal doesn’t support box characters | Use a simpler terminal or disable box drawing. |

---

## 13. Advanced Configuration

You can define a **preset board** in `config.txt` for predictable gameplay.

Example 3×3 board:

```txt
SIZE=3
BOARD=1,2,3,4,5,6,7,8,9
```

This will create:

```
1 2 3
4 5 6
7 8 9
```

Use `SEED` for reproducible random boards instead of manually defining one.

---

## 14. Conclusion

You are now ready to play the Row-Column Game! Experiment with different board sizes and computer strategies, challenge yourself, or let AIs battle it out. The game is simple to learn yet deep enough to reward planning and foresight. Have fun strategizing!
