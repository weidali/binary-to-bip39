import curses


def interactive_entropy_input(stdscr, total_bits: int) -> str:
    curses.curs_set(0)
    stdscr.nodelay(False)
    entropy = ""

    while True:
        stdscr.clear()

        entered = len(entropy)
        bar_width = 30
        filled = int(bar_width * entered / total_bits)
        bar = "█" * filled + "-" * (bar_width - filled)

        stdscr.addstr(0, 0, f"Interactive entropy input ({total_bits} bits)")
        stdscr.addstr(2, 0, f"[{bar}] {entered}/{total_bits}")
        stdscr.addstr(4, 0, "Controls:")
        stdscr.addstr(5, 0, "↑ = 1 | ↓ = 0 | 1 / 0")
        stdscr.addstr(6, 0, "Backspace = delete last bit")
        stdscr.addstr(7, 0, "Enter = finish (when complete)")

        if entered == total_bits:
            stdscr.addstr(9, 0, "Entropy complete. Press Enter to continue.")

        stdscr.refresh()
        key = stdscr.getch()

        if key in (curses.KEY_UP, ord("1")):
            if entered < total_bits:
                entropy += "1"

        elif key in (curses.KEY_DOWN, ord("0")):
            if entered < total_bits:
                entropy += "0"

        elif key in (curses.KEY_BACKSPACE, 127, 8):
            entropy = entropy[:-1]

        elif key in (10, 13):  # Enter
            if entered == total_bits:
                return entropy
