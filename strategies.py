from typing import Callable, List, Optional, Tuple
from board_manager import BoardManager, Position

# --- Type alias for strategy function signature -------------------------------
StrategyFunc = Callable[[BoardManager, Optional[Position]], Position]

# --- Utility: generic selector -------------------------------------------------
def _best_by_key(candidates: List[Position], key_fn: Callable[[Position], Tuple], reverse: bool = True) -> Position:
	"""Return the candidate with the best metric value according to key_fn."""
	best_pos: Optional[Position] = None
	best_key: Optional[Tuple] = None
	for pos in candidates:
		k = key_fn(pos)
		if best_key is None:
			best_key, best_pos = k, pos
			continue
		if (k > best_key) if reverse else (k < best_key):
			best_key, best_pos = k, pos
	return best_pos  # type: ignore

# --- Strategy 1: Greedy (maximize immediate value) -----------------------------
def strategy_greedy_maximize(board: BoardManager, last_pos: Optional[Position]) -> Position:
    '''
    Greedy strategy:
        • Always chooses the allowed cell with the highest immediate value.
        • Ignores future consequences.
        • Works for first move (all cells) and later moves (row/column).
    '''
    allowed = (board.get_all_available_positions()
               if last_pos is None else board.get_allowed_positions(last_pos))
    if not allowed:
        raise ValueError("No allowed moves for strategy")
    return _best_by_key(allowed, lambda p: (board.get_value(p) or 0,))

# --- Strategy 2: Maximize Future Minimum (1-step lookahead) --------------------
def strategy_maximize_future_min(board: BoardManager, last_pos: Optional[Position]) -> Position:
	'''
	Maximize-Future-Min strategy:
		• Looks two moves ahead.
		• For each possible move, assumes opponent then picks the biggest value available.
		• Chooses the move that maximizes (our_value - opponent_min_value).
		• Balances immediate gain and defense.
	'''
	allowed = (board.get_all_available_positions()
				if last_pos is None else board.get_allowed_positions(last_pos))
	if not allowed:
		raise ValueError("No allowed moves for strategy")

	def metric(pos: Position) -> Tuple[int, int]:
		val_now = board.get_value(pos) or 0
		# Simulate removal and compute opponent's weakest option
		r, c = pos
		saved = board.board[r][c]
		board.board[r][c] = None
		opp_options = board.get_allowed_positions(pos)
		min_opp_val = min((board.get_value(p) or 0) for p in opp_options) if opp_options else 0
		board.board[r][c] = saved
		return (val_now - min_opp_val, val_now)

	return _best_by_key(allowed, metric)

# --- Strategy 3: Minimize Opponent Options ------------------------------------
def strategy_minimize_opponent_options(board: BoardManager, last_pos: Optional[Position]) -> Position:
	'''
	Minimize-Opponent-Options strategy:
		• Chooses the move that leaves the fewest possible next moves for the opponent.
		• Tie-breaker: higher immediate value.
		• Focuses on board control rather than pure score.
	'''
	allowed = (board.get_all_available_positions()
				if last_pos is None else board.get_allowed_positions(last_pos))
	if not allowed:
		raise ValueError("No allowed moves for strategy")

	def metric(pos: Position) -> Tuple[int, int]:
		# Fewer opponent options is better; tie-break by our immediate value
		r, c = pos
		saved = board.board[r][c]
		board.board[r][c] = None
		opp_options = board.get_allowed_positions(pos)
		count = len(opp_options)
		board.board[r][c] = saved
		return (-count, board.get_value(pos) or 0)

	return _best_by_key(allowed, metric)

# --- Strategy 4: Preserve High Values -----------------------------------------
def strategy_high_value_preservation(board: BoardManager, last_pos: Optional[Position]) -> Position:
	'''
	High-Value-Preservation strategy:
		• Defensive approach focused on protecting the board's highest-value cells.
		• Simulates each move and counts how many max-value cells become visible to the opponent.
		• Prefers moves that avoid exposing the global maximum.
		• Tie-breaks by immediate value.
	'''
	allowed = (board.get_all_available_positions()
				if last_pos is None else board.get_allowed_positions(last_pos))
	if not allowed:
		raise ValueError("No allowed moves for strategy")
	global_max = board.max_remaining_value()

	def metric(pos: Position) -> Tuple[int, int, int]:
		r, c = pos
		saved = board.board[r][c]
		board.board[r][c] = None
		opp_options = board.get_allowed_positions(pos)

		# Track how many of opponent's allowed cells contain the global max
		contains_global_max = 0
		top_hits = 0
		for p in opp_options:
			val = board.get_value(p) or 0
			if val == global_max:
				contains_global_max = 1
				top_hits += 1
		board.board[r][c] = saved

		# Prefer no exposure to global max, then fewer hits, then higher own value
		return (-contains_global_max, -top_hits, board.get_value(pos) or 0)

	return _best_by_key(allowed, metric)

# --- Registry of available strategies -----------------------------------------
STRATEGY_REGISTRY: dict[str, StrategyFunc] = {
	"Greedy": strategy_greedy_maximize,
	"MaximizeFutureMin": strategy_maximize_future_min,
	"MinimizeOpponentOptions": strategy_minimize_opponent_options,
	"PreserveHighValues": strategy_high_value_preservation,
}

# --- Strategy lookup ----------------------------------------------------------
def get_strategy(name: str) -> StrategyFunc:
	"""Return a strategy function by its name."""
	if name not in STRATEGY_REGISTRY:
		raise ValueError(f"Unknown strategy: {name}")
	return STRATEGY_REGISTRY[name]
