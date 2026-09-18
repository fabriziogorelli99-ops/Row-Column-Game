import os
import sys
from typing import Optional, List
from game_engine import GameConfig, start_game
from scorekeeper import append_result, read_history


# --- Exceptions ---------------------------------------------------------------
class BackCommand(Exception):
    """Raised when user types 'Back' to go up one level."""
    pass

# --- Input helper -------------------------------------------------------------
def guarded_input(prompt: str = "") -> str:
    """Unified input: raises KeyboardInterrupt on 'Menu' (to exit to main menu) and exits on 'Exit'."""
    s = input(prompt)
    t = s.strip().lower()
    if t == "menu":
        # Jump to Main Menu (handled in main())
        raise KeyboardInterrupt
    if t == "back":
        # Pop one level up (handled in config menu/submenus)
        raise BackCommand
    if t == "exit":
        print("Goodbye!")
        sys.exit(0)
    return s

# --- Config file handling -----------------------------------------------------
def _parse_int_list(csv: str) -> List[int]:
    """ Parse comma-separated integers into a list."""
    parts = [p.strip() for p in csv.split(",") if p.strip()] 
    return [int(p) for p in parts]

def load_config(path: str) -> GameConfig:
    """Load configuration values from config.txt."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Config file not found: {path}")

    size: Optional[int] = None
    mode: Optional[str] = None
    a_strategy: Optional[str] = None
    b_strategy: Optional[str] = None
    seed: Optional[int] = None
    preset_board: Optional[List[int]] = None
    start_player: str = "A"
    board_source: Optional[str] = None  # "RANDOM" or "MANUAL"

    # Parse key-value pairs
    with open(path, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = [x.strip() for x in line.split("=", 1)]
            key_up = key.upper()
            if key_up == "SIZE":
                size = int(value)
            elif key_up == "MODE":
                mode = value
            elif key_up == "A_STRATEGY":
                a_strategy = value
            elif key_up == "B_STRATEGY":
                b_strategy = value
            elif key_up == "SEED":
                seed = int(value)
            elif key_up == "BOARD":
                preset_board = _parse_int_list(value)
            elif key_up == "START_PLAYER":
                start_player = (value or "A").strip().upper()
            elif key_up == "HUMAN_PLAYER":
                human_player = value.strip().upper()
            elif key_up == "BOARD_SOURCE":
                board_source = value.strip().upper()

    if size is None:
        raise ValueError("SIZE must be set in config.txt")
    if mode is None:
        mode = "H_VS_C"

    # Infer BOARD_SOURCE if missing for backward compatibility
    if board_source not in {"RANDOM", "MANUAL"}:
        if preset_board is not None:
            board_source = "MANUAL"
        else:
            board_source = "RANDOM"

    # Enforce precedence: MANUAL means ignore SEED
    if board_source == "MANUAL":
        seed_to_use = None
        preset_to_use = preset_board
    else:
        seed_to_use = seed
        preset_to_use = None  # ensure random is used

    return GameConfig(
        size=size,
        mode=mode,
        a_strategy=a_strategy,
        b_strategy=b_strategy,
        seed=seed_to_use,
        preset_board=preset_to_use,
        start_player=start_player or "A",
        human_player=human_player if 'human_player' in locals() else None,
    )

def save_config(path: str, config: GameConfig, *,
                board_source: str,
                seed_raw: Optional[int],
                preset_board_raw: Optional[List[int]]) -> None:
    """Save configuration values to config.txt.

    Note: we write both SEED and BOARD, but BOARD_SOURCE determines which is used.
    """
    lines = [
        "Row-Column Game configuration",
        "SIZE must be provided. MODE can be H_VS_H, H_VS_C, or C_VS_C",
        "A_STRATEGY/B_STRATEGY are names from strategies.py when the player is a computer",
        "",
        f"SIZE={config.size}",
        f"MODE={config.mode}",
        f"START_PLAYER={config.start_player}",
        f"BOARD_SOURCE={board_source}",
    ]
    if config.mode == "H_VS_C":
        lines.append(f"HUMAN_PLAYER={(getattr(config, 'human_player', 'A')).upper()}")
    if config.a_strategy:
        lines.append(f"A_STRATEGY={config.a_strategy}")
    if config.b_strategy:
        lines.append(f"B_STRATEGY={config.b_strategy}")

    # Persist raw values (not the precedence-resolved ones) so user can switch later
    if seed_raw is not None:
        lines.append(f"SEED={seed_raw}")
    if preset_board_raw:
        board_str = ",".join(str(v) for v in preset_board_raw)
        lines.append(f"BOARD={board_str}")

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

# --- UI helper ---------------------------------------------------------------
def clear_screen() -> None:
    """Clear terminal screen."""
    if sys.platform == "win32":
        os.system("cls")
    else:
        os.system("clear")
        
# --- Main menu viewer ----------------------------------------------------------

def show_main_menu() -> None:
    """Draw the main menu layout."""
    clear_screen()
    print("=" * 50)
    print("     Row-Column Game (RC-Game)")
    print("=" * 50)
    print("\n1. Play\n2. Adjust Config\n3. History\n4. Exit\n")
    print("=" * 50)

# --- History viewer -----------------------------------------------------------

def show_history() -> None:
    """History viewer: shows saved match results through read_history."""
    clear_screen()
    print("=" * 80)
    print("                 History")
    print("=" * 80)
    rows = read_history()   
    if not rows:
        print("\nNo saved games yet.\n")
        print("=" * 80)
        try:
            guarded_input("Press Enter (or 'Back') to return... ")
        except BackCommand:
            pass
        return

    # Show last 20 games by default 
    to_show = rows[-20:] if len(rows) > 20 else rows
    print("\nShowing up to the last 20 results:\n")
    for i, r in enumerate(to_show, 1):
        print(f"{i:>2}. {r['date']} | {r['match']} | A:{r['a_score']} B:{r['b_score']} | "
              f"Winner:{r['winner']} | Rounds:{r['rounds']} | Mode:{r['mode']}")
    print("\n" + "=" * 80)
    try:
        guarded_input("Press Enter (or 'Back') to return... ")
    except BackCommand:
        pass

# --- Submenus for Configs 1, 2, 3, 4, 5, 6 -----------------
def submenu_board_size(config: GameConfig, state: dict) -> None:
    """Option 1: Board Size submenu."""
    while True:
        clear_screen()
        print("=" * 50)
        print("            Board Size")
        print("=" * 50)
        print(f"\nCurrent size: {config.size}")
        print("\nEnter a new size (integer >= 2), or 'Back' / 'Menu' / 'Exit'.")
        print("=" * 50)
        try:
            raw = guarded_input("New size: ")
            new_size = int(raw.strip())
            if new_size < 2:
                print("Size must be ≥2. Press Enter to continue...")
                guarded_input("")
                return
            config.size = new_size
            # If manual board exists but length mismatches new size, warn & clear
            pb = state.get("preset_board_raw")
            if pb and len(pb) != new_size * new_size:
                print("Existing manual BOARD length no longer matches SIZE; clearing manual BOARD and switching to RANDOM.")
                state["preset_board_raw"] = None
                state["board_source"] = "RANDOM"
                print("Press Enter to continue...")
                try:
                    guarded_input("")
                except BackCommand:
                    pass
            return
        except BackCommand:
            return
        except ValueError:
            print("Invalid integer. Press Enter to continue...")
            try:
                guarded_input("")
            except BackCommand:
                pass

def submenu_game_mode(config: GameConfig) -> None:
    """Option 2: Game Mode submenu (accepts 1/2/3 or names)."""
    while True:
        clear_screen()
        print("=" * 50)
        print("            Game Mode")
        print("=" * 50)
        print(f"\nCurrent: {config.mode}")
        print("\n1) H_VS_H  (Human vs Human)")
        print("2) H_VS_C  (Human vs Computer)")
        print("3) C_VS_C  (Computer vs Computer)")
        print("\nNotes:")
        print("Enter 1/2/3 or a mode name, or 'Back' / 'Menu' / 'Exit'.")
        print("=" * 50)

        try:
            raw = guarded_input("Choice: ").strip().upper()
            mapping = {"1": "H_VS_H", "2": "H_VS_C", "3": "C_VS_C"}
            new_mode = mapping.get(raw, raw)
            if new_mode in {"H_VS_H", "H_VS_C", "C_VS_C"}:
                config.mode = new_mode
                if new_mode == "H_VS_C" and not hasattr(config, "human_player"):
                    config.human_player = "A"  # default to A if not set
                return
            else:
                print("Invalid mode. Press Enter to continue...")
                guarded_input("")
        except BackCommand:
            return

def _strategy_submenu_generic(which: str, get_attr, set_attr) -> None:
    """Shared submenu for Player A/B Strategy (accepts number or name)."""
    STRATS = ["Greedy", "MaximizeFutureMin", "MinimizeOpponentOptions", "PreserveHighValues"]
    while True:
        clear_screen()
        print("=" * 50)
        print(f"            {which} Strategy")
        print("=" * 50)
        current = get_attr()
        print(f"\nCurrent: {current or 'Human'}")
        print("\n0) Human")
        for i, s in enumerate(STRATS, start=1):
            print(f"{i}) {s}")
        print("\nNotes:")
        print("Enter 0/1/2/3/4 or a strategy name, or 'Back' / 'Menu' / 'Exit'.")
        print("=" * 50)

        try:
            raw = guarded_input("Choice: ").strip()
            raw_u = raw.upper()
            # numeric path
            if raw_u in {"0", "1", "2", "3", "4"}:
                idx = int(raw_u)
                if idx == 0:
                    set_attr(None)
                else:
                    set_attr(STRATS[idx - 1])
                return
            # textual path
            if raw_u in {"HUMAN", ""}:
                set_attr(None)
                return
            if raw in STRATS:
                set_attr(raw)
                return
            print("Invalid choice. Press Enter to continue...")
            guarded_input("")
        except BackCommand:
            return

def submenu_strategy_A(config: GameConfig) -> None:
    """Option 3: Player A Strategy submenu."""
    _strategy_submenu_generic(
        "Player A",
        get_attr=lambda: config.a_strategy,
        set_attr=lambda v: setattr(config, "a_strategy", v),
    )
    if config.mode == "H_VS_C":
        if config.b_strategy is None:
            config.human_player = "B"
        elif config.a_strategy is None:
            config.human_player = "A"


def submenu_strategy_B(config: GameConfig) -> None:
    """Option 4: Player B Strategy submenu."""
    _strategy_submenu_generic(
        "Player B",
        get_attr=lambda: config.b_strategy,
        set_attr=lambda v: setattr(config, "b_strategy", v),
    )
    if config.mode == "H_VS_C":
        if config.b_strategy is None:
            config.human_player = "B"
        elif config.a_strategy is None:
            config.human_player = "A"


def board_presets_menu(config: GameConfig,
                       state: dict) -> None:
    """
    Option 5: Board Presets submenu
    
    Let user choose Random vs Manual board, set/clear seed, set/clear manual board.
    We keep small 'state' dict to persist raw values for saving:
      - state['board_source']: 'RANDOM' | 'MANUAL'
      - state['seed_raw']: Optional[int]
      - state['preset_board_raw']: Optional[List[int]]
    """
    while True:
        clear_screen()
        src = state.get("board_source", "RANDOM")
        seed_raw = state.get("seed_raw", None)
        preset_raw = state.get("preset_board_raw", None)
        size = config.size

        print("=" * 50)
        print("            Board Presets")
        print("=" * 50)
        print(f"\nCurrent source: {src}")
        if src == "RANDOM":
            print(f"Seed (used): {seed_raw if seed_raw is not None else 'None'}")
            print("Manual board is ignored while source is RANDOM.")
        else:
            preview = f"{len(preset_raw)} values" if preset_raw else "None"
            print(f"Manual BOARD (used): {preview}")
            print("Seed is ignored while source is MANUAL.")
        print("\nOptions:")
        print("  1) Use RANDOM board")
        print("  2) Use MANUAL board")
        print("  3) Set random SEED")
        print("  4) Set MANUAL BOARD values")
        print("  5) Clear MANUAL BOARD")
        print("  6) Back")
        print("\nNotes:")
        print(f"- Manual board must contain exactly {size*size} integers (comma-separated).")
        print("- When source is MANUAL, SEED is ignored.")
        print("=" * 50)

        try:
            choice = guarded_input("Enter choice (1-6): ")
        except BackCommand:
            return

        if choice == "1":
            state["board_source"] = "RANDOM"
        elif choice == "2":
            state["board_source"] = "MANUAL"
            if not state.get("preset_board_raw"):
                print(f"\nYou selected MANUAL but no board is set yet.")
                print(f"Enter {size*size} comma-separated ints to set it now, or type 'Back' to skip.")
                try:
                    raw = guarded_input("BOARD= ")
                    vals = _parse_int_list(raw)
                    if len(vals) != size * size:
                        print(f"Invalid length. Expected {size*size} values. Press Enter to continue...")
                        try:
                            guarded_input("")
                        except BackCommand:
                            pass
                    else:
                        state["preset_board_raw"] = vals
                except BackCommand:
                    pass
        elif choice == "3":
            print("\n(Set SEED used only when source is RANDOM)")
            try:
                raw = guarded_input("Enter seed (empty/None to clear): ").strip()
                if raw == "" or raw.lower() == "none":
                    state["seed_raw"] = None
                else:
                    state["seed_raw"] = int(raw)
            except BackCommand:
                pass
            except ValueError:
                print("Invalid seed. Press Enter to continue...")
                try:
                    guarded_input("")
                except BackCommand:
                    pass
        elif choice == "4":
            print(f"\nEnter exactly {size*size} comma-separated integers.")
            try:
                raw = guarded_input("BOARD= ")
                vals = _parse_int_list(raw)
                if len(vals) != size * size:
                    print(f"Invalid length. Expected {size*size} values. Press Enter to continue...")
                    try:
                        guarded_input("")
                    except BackCommand:
                        pass
                else:
                    state["preset_board_raw"] = vals
                    state["board_source"] = "MANUAL"
            except BackCommand:
                pass
            except ValueError:
                print("Invalid BOARD list. Press Enter to continue...")
                try:
                    guarded_input("")
                except BackCommand:
                    pass
        elif choice == "5":
            state["preset_board_raw"] = None
            state["board_source"] = "RANDOM"
            print("Manual board cleared. Source set to RANDOM. Press Enter to continue...")
            try:
                guarded_input("")
            except BackCommand:
                pass
        elif choice == "6":
            return
        else:
            print("Invalid choice. Press Enter to continue...")
            try:
                guarded_input("")
            except BackCommand:
                pass
            
def submenu_start_player(config: GameConfig) -> None:
    """Option 6: Start Player submenu (accepts 1/2 or A/B)."""
    while True:
        clear_screen()
        print("=" * 50)
        print("            Start Player")
        print("=" * 50)
        print(f"\nCurrent: {config.start_player}")
        print("\n1) A")
        print("2) B")
        print("\nNotes:")
        print("Enter 1/2 or A/B, or 'Back' / 'Menu' / 'Exit'.")
        print("=" * 50)
        try:
            raw = guarded_input("Choice: ").strip().upper()
            mapping = {"1": "A", "2": "B", "A": "A", "B": "B"}
            if raw in mapping:
                config.start_player = mapping[raw]
                return
            else:
                print("Invalid choice. Press Enter to continue...")
                guarded_input("")
        except BackCommand:
            return

# --- Config menu --------------------------------------------------------------
def show_config_menu(config: GameConfig,
                     state: dict) -> bool:
    """Interactive configuration menu.
    Returns True if user saves, False if cancel.
    'Menu' → return to main menu
    'Back' → go up one level
    """
    while True:
        # Display current settings (Board Presets summary UNCHANGED)
        clear_screen()
        print("=" * 50)
        print("     Configuration Settings")
        print("=" * 50)
        print(f"\n1. Board Size (SIZE): {config.size}")
        print(f"2. Game Mode (MODE): {config.mode}")
        print(f"3. Player A Strategy: {config.a_strategy or 'Human'}")
        print(f"4. Player B Strategy: {config.b_strategy or 'Human'}")
        # Board Presets summary
        src = state.get("board_source", "RANDOM")
        seed_raw = state.get("seed_raw", None)
        preset_raw = state.get("preset_board_raw", None)
        if src == "RANDOM":
            summary = f"RANDOM (seed={seed_raw if seed_raw is not None else 'None'})"
        else:
            count = len(preset_raw) if preset_raw else 0
            summary = f"MANUAL ({count} values)"
        print(f"5. Board Presets: {summary}")
        print(f"6. Start Player: {config.start_player}")
        print("7. Save and Return to Main Menu")
        print("8. Cancel (Return without saving)")
        print("\nType 'Back' to return, 'Menu' for main menu, or 'Exit' to quit.")
        print("=" * 50)

        try:
            choice = guarded_input("Enter choice (1-8): ")
        except BackCommand:
            return False

        if choice == "1":
            submenu_board_size(config, state)
        elif choice == "2":
            submenu_game_mode(config)
        elif choice == "3":
            submenu_strategy_A(config)
        elif choice == "4":
            submenu_strategy_B(config)
        elif choice == "5":
            try:
                board_presets_menu(config, state)  
            except BackCommand:
                pass
        elif choice == "6":
            submenu_start_player(config)
        elif choice == "7":
            # --- Validate strategies against mode before saving ---
            mode = (config.mode or "").upper()
            a_is_human = (config.a_strategy is None)
            b_is_human = (config.b_strategy is None)

            def _block(msg: str) -> None:
                print(f"\nCannot save: {msg}")
                print("Press Enter to continue...")
                try:
                    guarded_input("")
                except BackCommand:
                    pass

            if mode == "H_VS_H":
                # Both must be Human
                if not a_is_human or not b_is_human:
                    _block("In H_VS_H mode, both players must be Human (leave strategies blank).")
                    continue

            elif mode == "H_VS_C":
                # Exactly one Human, one Strategy
                if (a_is_human and b_is_human) or (not a_is_human and not b_is_human):
                    _block("In H_VS_C mode, exactly one player must be Human and the other must have a strategy.")
                    continue

            elif mode == "C_VS_C":
                # Both must be strategies (no Human)
                if a_is_human or b_is_human:
                    _block("In C_VS_C mode, both players must have strategies (no Human).")
                    continue

            else:
                _block("Unknown MODE. Choose H_VS_H, H_VS_C, or C_VS_C.")
                continue

            # --- Passed validation: proceed to save ---
            board_source = state.get("board_source", "RANDOM")
            seed_raw = state.get("seed_raw", None)
            preset_board_raw = state.get("preset_board_raw", None)
            save_config(
                os.path.join(os.path.dirname(__file__), "config.txt"),
                config,
                board_source=board_source,
                seed_raw=seed_raw,
                preset_board_raw=preset_board_raw
            )
            return True
        
        elif choice == "8":
            # Cancel
            return False

# --- Main loop ---------------------------------------------------------------
def main() -> None:
    """Main program loop: handles Play, Config, Exit."""
    config_path = os.path.join(os.path.dirname(__file__), "config.txt")

    """
    This state holds raw values for saving and the user's preset selection.
    We populate it from the loaded config (and file contents) before editing.
    Defaults assume RANDOM with no seed.
    """
    state = {
        "board_source": "RANDOM",
        "seed_raw": None,
        "preset_board_raw": None,
    }

    while True:
        show_main_menu()
        try:
            choice = guarded_input("Enter choice (1-4): ")
        except KeyboardInterrupt:
            continue

        if choice == "1":
            # Play
            try:
                config = load_config(config_path)
                # Run a game and get its summary (dict with a_score, b_score, rounds, mode, result)
                result = start_game(config)
                
                # If user typed 'menu' during the game, skip post-game menu and go straight back.
                if result is None:
                    continue  #Bback to main loop 

                # --- End-of-game actions UI (shown AFTER the game_engine's own 'Press Enter') ---
                def _save_history(config, result):
                    # Ask names (trim to 24 chars, default A/B)
                    name_a = input("Enter Player A name (default 'A'): ").strip()[:24] or "A"
                    name_b = input("Enter Player B name (default 'B'): ").strip()[:24] or "B"

                    # Use centralized CSV writer (scorekeeper.append_result)
                    append_result(
                        match=f"{name_a} VS {name_b}",
                        a_score=int(result.get("a_score", 0)),
                        b_score=int(result.get("b_score", 0)),
                        winner=result.get("winner", "Tie"),
                        rounds=int(result.get("rounds", 0)),
                        mode=str(result.get("mode", "")),
                    )

                    print("Saved to history.csv. Press Enter to continue...")
                    guarded_input("")

                while True:
                    clear_screen()
                    print("=" * 50)
                    print("          Post Game Options")
                    print("=" * 50)
                    print("\n  1) Play again")
                    print("  2) Save")
                    print("  3) Main menu")
                    print("\nNotes:")
                    print("Enter 1/2/3 or 'Play again'/'Save'/'Menu', or press Enter to return to main menu.")
                    print("=" * 50)
                    print()
                    try:
                        sel = guarded_input("Choice: ").strip().lower()
                    except KeyboardInterrupt:
                        break

                    if sel in {"", "3", "menu"}:
                        # back to main menu
                        break
                    elif sel in {"1", "play again"}:
                        result = start_game(config)  # run again with the same config
                        continue
                    elif sel in {"2", "save"}:
                        _save_history(config, result)
                        continue
                    else:
                        print("Invalid choice. Press Enter to continue...")
                        try:
                            guarded_input("")
                        except KeyboardInterrupt:
                            break
                        # loop back and redraw the same post-game menu

            except KeyboardInterrupt:
                pass
            except Exception as e:
                print(f"\nError: {e}")
                print("Press Enter to continue...")
                try:
                    guarded_input("")
                except KeyboardInterrupt:
                    pass

        elif choice == "2":
            # Adjust Config
            try:
                # Re-read raw file to seed 'state' so we preserve SEED/BOARD even if inactive.
                state = {
                    "board_source": "RANDOM",
                    "seed_raw": None,
                    "preset_board_raw": None,
                }
                if os.path.exists(config_path):
                    with open(config_path, "r", encoding="utf-8") as f:
                        for raw in f:
                            line = raw.strip()
                            if not line or line.startswith("#") or "=" not in line:
                                continue
                            key, value = [x.strip() for x in line.split("=", 1)]
                            k = key.upper()
                            if k == "BOARD_SOURCE":
                                state["board_source"] = value.strip().upper()
                            elif k == "SEED":
                                try:
                                    state["seed_raw"] = int(value.strip())
                                except Exception:
                                    state["seed_raw"] = None
                                    
                            elif k == "BOARD":
                                try:
                                    state["preset_board_raw"] = _parse_int_list(value)
                                except Exception:
                                    state["preset_board_raw"] = None
                                    

                cfg = load_config(config_path)

                try:
                    show_config_menu(cfg, state)
                except KeyboardInterrupt:
                    continue
                
                if show_config_menu(cfg, state):
                    print("\nConfiguration saved! Press Enter to continue...")
                    try:
                        guarded_input("")
                    except KeyboardInterrupt:
                        pass
            except Exception as e:
                print(f"\nError: {e}")
                print("Press Enter to continue...")
                try:
                    guarded_input("")
                except KeyboardInterrupt:
                    pass

        elif choice == "3":
            # History viewer
            try:
                show_history()
            except KeyboardInterrupt:
                pass

        elif choice == "4":
            # Exit
            print("\nGoodbye!")
            break

        else:
            print("\nInvalid choice. Press Enter to continue...")
            try:
                guarded_input("")
            except KeyboardInterrupt:
                pass

if __name__ == "__main__":
    main()
