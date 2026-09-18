import random
from typing import List, Optional, Tuple

# --- Type alias for coordinates -----------------------------------------------
Position = Tuple[int, int]


# --- Board Manager class ------------------------------------------------------
class BoardManager:
    """Manages the game board state and all related operations."""

    def __init__(self, size: int, seed: Optional[int] = None, preset_board: Optional[List[int]] = None) -> None:
        # Board setup and random generator
        self.size = size
        self.random = random.Random(seed)
        self.board: List[List[Optional[int]]] = self._init_board(preset_board)
        # Track the most recently removed cell for display (the only one marked 'X')
        self.last_removed_pos: Optional[Position] = None

    # --- Board initialization -------------------------------------------------
    def _init_board(self, preset_board: Optional[List[int]]) -> List[List[Optional[int]]]:
        """Create initial board (random or from preset values)."""
        if preset_board is not None:
            expected = self.size * self.size
            if len(preset_board) != expected:
                raise ValueError(f"Preset board length {len(preset_board)} != {expected}")
            grid: List[List[Optional[int]]] = []
            idx = 0
            for _ in range(self.size):
                row: List[Optional[int]] = []
                for _ in range(self.size):
                    row.append(int(preset_board[idx]))
                    idx += 1
                grid.append(row)
            return grid

        # Generate random numbers (1–9)
        return [[self.random.randint(1, 9) for _ in range(self.size)] for _ in range(self.size)]

    # --- Position checks ------------------------------------------------------
    def in_bounds(self, pos: Position) -> bool:
        """Check if position lies inside the board."""
        r, c = pos
        return 0 <= r < self.size and 0 <= c < self.size

    def is_available(self, pos: Position) -> bool:
        """Check if cell exists and hasn't been removed."""
        r, c = pos
        return self.in_bounds(pos) and self.board[r][c] is not None

    # --- Cell value access ----------------------------------------------------
    def get_value(self, pos: Position) -> Optional[int]:
        """Return the cell's value, or None if removed."""
        r, c = pos
        return self.board[r][c]

    def remove_and_get(self, pos: Position) -> int:
        """Remove a cell and return its value. Marks cell as the latest removal."""
        if not self.is_available(pos):
            raise ValueError("Attempted to remove unavailable position")
        r, c = pos
        val = self.board[r][c]
        self.board[r][c] = None
        self.last_removed_pos = (r, c)  # Track latest removal for display
        return int(val)  # type: ignore

    # --- Board state queries --------------------------------------------------
    def any_available(self) -> bool:
        """Return True if at least one cell remains on the board."""
        for r in range(self.size):
            for c in range(self.size):
                if self.board[r][c] is not None:
                    return True
        return False

    def get_all_available_positions(self) -> List[Position]:
        """List all cells that still contain values."""
        out: List[Position] = []
        for r in range(self.size):
            for c in range(self.size):
                if self.board[r][c] is not None:
                    out.append((r, c))
        return out

    def get_allowed_positions(self, last_pos: Position) -> List[Position]:
        """Return all positions allowed for the next move (same row or column)."""
        r0, c0 = last_pos
        allowed: List[Position] = []
        # Same row
        for c in range(self.size):
            if self.board[r0][c] is not None:
                allowed.append((r0, c))
        # Same column (skip the intersection cell to avoid duplicate)
        for r in range(self.size):
            if r != r0 and self.board[r][c0] is not None:
                allowed.append((r, c0))
        return allowed

    # --- Basic text display ---------------------------------------------------
    def print_board(self) -> None:
        """Simple grid print (removed cells are blank except latest one marked 'X')."""
        for r in range(self.size):
            row_str: List[str] = []
            for c in range(self.size):
                val = self.board[r][c]
                if val is None:
                    cell = 'X' if self.last_removed_pos == (r, c) else ' '
                else:
                    cell = str(val)
                row_str.append(cell)
            print(' '.join(row_str))

    # --- Fancy boxed display --------------------------------------------------
    def print_board_boxed(self, round_num: int = 0) -> None:
        """Pretty ASCII board with coordinates, round number, and matrix size box."""
        # --- Width calculations ---
        board_inner_width = self.size * 2 - 1
        matrix_size_str = f"{self.size}x{self.size}"
        row_num_box_width = 5  # │ n │ box width
        outer_width = board_inner_width + row_num_box_width + 6

        # --- Round title box ---
        round_str = f"Round {round_num}"
        round_box_width = max(len(round_str) + 2, outer_width - 2)
        pad = (round_box_width - len(round_str) - 2) // 2
        extra = (round_box_width - len(round_str) - 2) % 2
        print("   ┌" + "─" * (round_box_width - 2) + "┐")
        print("   │" + " " * pad + round_str + " " * (pad + extra) + "│")
        print("   └" + "─" * (round_box_width - 2) + "┘")

        # --- Outer top border ---
        print("   ┌" + "─" * (outer_width - 2) + "┐")

        # --- Column headers + matrix size box ---
        col_nums_str = " ".join(str(c + 1) for c in range(self.size))
        col_box_width = len(col_nums_str) + 2
        matrix_box_width = len(matrix_size_str) + 2

        # Header line tops
        line = f"   │ ┌" + "─" * (col_box_width - 2) + "┐┌" + "─" * (matrix_box_width - 2) + "┐"
        line += " " * max(0, outer_width - len(line) + 2) + "│"
        print(line)
        # Header values
        line = f"   │ │{col_nums_str}││{matrix_size_str}│"
        line += " " * max(0, outer_width - len(line) + 2) + "│"
        print(line)
        # Header bottoms
        line = f"   │ └" + "─" * (col_box_width - 2) + "┘└" + "─" * (matrix_box_width - 2) + "┘"
        line += " " * max(0, outer_width - len(line) + 2) + "│"
        print(line)

        # --- Board top border ---
        line = "   │ ┌" + "─" * board_inner_width + "┐┌" + "─" * (row_num_box_width - 2) + "┐"
        line += " " * max(0, outer_width - len(line) + 2) + "│"
        print(line)

        # --- Board rows with numbers ---
        for r in range(self.size):
            cells: List[str] = []
            for c in range(self.size):
                val = self.board[r][c]
                if val is None:
                    cell = 'X' if self.last_removed_pos == (r, c) else ' '
                else:
                    cell = str(val)
                cells.append(cell)
            row_content = " ".join(cells)
            row_num = f"{r + 1:^3}"
            line = f"   │ │{row_content}││{row_num}│"
            line += " " * max(0, outer_width - len(line) + 2) + "│"
            print(line)

        # --- Board bottom border ---
        line = "   │ └" + "─" * board_inner_width + "┘└" + "─" * (row_num_box_width - 2) + "┘"
        line += " " * max(0, outer_width - len(line) + 2) + "│"
        print(line)

        # --- Outer bottom border ---
        print("   └" + "─" * (outer_width - 2) + "┘")

    # --- Utility: find largest remaining value --------------------------------
    def max_remaining_value(self) -> int:
        """Return the highest value still present on the board."""
        max_val = 0
        for r in range(self.size):
            for c in range(self.size):
                val = self.board[r][c]
                if val is not None and val > max_val:
                    max_val = val
        return max_val
