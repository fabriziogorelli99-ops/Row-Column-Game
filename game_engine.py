import os
import sys
from typing import Callable, Optional, Tuple, Any  

from board_manager import BoardManager, Position
from strategies import get_strategy

# --- Configuration Data Transfer Object -------------------------------------------
class GameConfig:
    """Simple container for game settings (size, mode, strategies, seed, preset board)."""

    def __init__(
        self,
        size: int,
        mode: str,
        a_strategy: Optional[str],
        b_strategy: Optional[str],
        seed: Optional[int],
        preset_board: Optional[list[int]],
        start_player: str = "A",
        human_player: Optional[str] = None,
    ):
        self.size = size
        self.mode = mode
        self.a_strategy = a_strategy
        self.b_strategy = b_strategy
        self.seed = seed
        self.preset_board = preset_board
        self.start_player = (start_player or "A").upper()
        if self.start_player not in {"A", "B"}:
            self.start_player = "A"
        self.human_player = (human_player or "A").upper() if human_player else None
        

# --- Input parsing helpers ----------------------------------------------------
def _parse_move_input(raw: str) -> Optional[Position]:
    """Parse 'row,col' (1-indexed) into 0-indexed (r, c) tuple; return None on error."""
    try:
        parts = raw.strip().split(',')
        if len(parts) != 2:
            return None
        r = int(parts[0].strip()) - 1
        c = int(parts[1].strip()) - 1
        return (r, c)
    except Exception:
        return None

def _guarded_input(prompt: str) -> Optional[str]:
    """
    Unified input: returns None on 'Menu' (to exit to main menu) and exits on 'Exit'.
    This guarded input does not handle "back" commands. 
    """
    s = input(prompt)
    t = s.strip().lower()
    if t == 'menu':
        raise KeyboardInterrupt
    if s.strip().lower() == 'exit':
        print("Goodbye!")
        sys.exit(0)
    return s

# --- UI helpers ---------------------------------------------------------------
def _clear_terminal() -> None:
    """Clear the terminal screen (cross-platform)."""
    if sys.platform == 'win32':
        os.system('cls')
    else:
        os.system('clear')

def _print_scores(a_score: int, b_score: int) -> None:
    """Print current score line."""
    print(f"Score A: {a_score} | Score B: {b_score}")

# --- Game loop ----------------------------------------------------------------
def start_game(config: GameConfig) -> Optional[dict[str, Any]]:
    """Run a single game session using the provided configuration.

    Returns:
        A summary dict on normal game completion:
          {
            "a_score": int,
            "b_score": int,
            "rounds": int,
            "mode": str,
            "winner": "A" | "B" | "Tie",
          }
        or None if the user typed 'Menu' mid-game.
    """
    # --- Initialize board and validate mode ---
    board = BoardManager(config.size, seed=config.seed, preset_board=config.preset_board)
    mode = (config.mode or '').upper()
    if mode not in {"H_VS_H", "H_VS_C", "C_VS_C"}:
        raise ValueError("MODE must be one of H_VS_H, H_VS_C, C_VS_C")

    # --- Player controllers (human or strategy func) ---
    PlayerController = Tuple[str, Optional[Callable[[BoardManager, Optional[Position]], Position]]]
    """ A tuple of ('human', None) or ('computer', strategy_func) """
    
    def controller_for(player: str) -> PlayerController: # type: ignore
        """Return ('human', None) or ('computer', strategy_func) based on mode/config."""
        
        if mode == "H_VS_H":
            return ("human", None)

        if mode == "H_VS_C":
            human = (getattr(config, "human_player", None) or "A").upper()
            if human not in ("A", "B"):
                raise ValueError("HUMAN_PLAYER must be A or B for H_VS_C")

            if player == human:
                return ("human", None)
            else:
                strat_name = config.a_strategy if player == "A" else config.b_strategy
                if not strat_name:
                    raise ValueError(f"{player}_STRATEGY must be set for H_VS_C when {player} is computer")
                return ("computer", get_strategy(strat_name))

        if mode == "C_VS_C":
            if not config.a_strategy or not config.b_strategy:
                raise ValueError("A_STRATEGY and B_STRATEGY must be set for C_VS_C")
            return ("computer", get_strategy(config.a_strategy if player == "A" else config.b_strategy))

        raise ValueError("Invalid MODE")

    ctrl_A = controller_for('A')
    ctrl_B = controller_for('B')

    # --- Score and round state ---
    """ Initialize scores and round number values. """
    a_score = 0
    b_score = 0
    round_num = 1

    # --- First player and initial state ---
    last_pos: Optional[Position] = None
    current = (config.start_player or "A").upper()

    _clear_terminal()
    print("Initial board:")
    board.print_board_boxed(round_num)

    # --- Main turn loop ---
    while True:
        # Allowed cells: all if first move, otherwise row/column of last_pos
        if last_pos is None:
            allowed = board.get_all_available_positions()
        else:
            allowed = board.get_allowed_positions(last_pos)

        if not allowed:
            _clear_terminal()
            board.print_board_boxed(round_num)  # show the last board state
            print("Final Board. No moves available. Game over.")
            break

        _clear_terminal()
        board.print_board_boxed(round_num)
        _print_scores(a_score, b_score) 
        if last_pos is None:
            print(f"Player {current}'s turn. Allowed: {len(allowed)} cells (any cell for the first move).")
        else:
            print(f"Player {current}'s turn. Allowed: {len(allowed)} cells in row {last_pos[0]+1} or col {last_pos[1]+1}.")

        # Determine player type and strategy
        ptype, strat = ctrl_A if current == 'A' else ctrl_B
        move: Optional[Position] = None

        # --- Human player ---
        if ptype == 'human':
            while True:
                raw = _guarded_input("Enter move as Row,Col (1-indexed): ")
                pos = _parse_move_input(raw)
                if pos is None:
                    print("Invalid format. Use r,c like 2,3"); continue
                if not board.in_bounds(pos):
                    print("Out of bounds. Try again."); continue
                if not board.is_available(pos):
                    print("Cell already taken. Try again."); continue
                if last_pos is not None:
                    r0, c0 = last_pos
                    if not (pos[0] == r0 or pos[1] == c0):
                        print("Must choose from same row or column as opponent's last move.")
                        continue
                move = pos
                break

        # --- Computer player ---
        else:
            if strat is None:
                raise RuntimeError("Missing strategy for computer player")
            move = strat(board, last_pos)

        # --- Execute move ---
        val_now = board.remove_and_get(move)
        if current == 'A':
            a_score += val_now
        else:
            b_score += val_now

        # Advance round and update display
        round_num += 1
        _clear_terminal()
        print(f"{current} chose (row {move[0]+1}, col {move[1]+1}) = {val_now}")
        board.print_board_boxed(round_num)
        _print_scores(a_score, b_score)

        # Prepare for next turn
        last_pos = move
        current = 'A' if current == 'B' else 'B'

    # --- Game over summary ---
    print("\nFinal scores:")
    _print_scores(a_score, b_score)
    if a_score > b_score:
        winner = "A"
        print("Winner: A")
    elif b_score > a_score:
        winner = "B"
        print("Winner: B")
    else:
        winner = "Tie"
        print("Tie")
        
    _guarded_input("\nPress Enter to continue...")

    return {
        "a_score": a_score,
        "b_score": b_score,
        "rounds": round_num,
        "mode": mode,
        "winner": winner,
    }
