"""
Sprite rendering inside curses using ▀ half-blocks + xterm-256 colour pairs.
Each sprite is 8 pixels wide × 8 pixels tall = 8 cols × 4 terminal rows.

Requires COLORS >= 256.  Falls back to a plain @ if the terminal only has 8/16.
"""

import curses

DARK  = (12, 12, 18)   # fill colour for transparent pixels
EMPTY = None           # transparent sentinel — use EMPTY, never _ (name clash risk)

# Dynamic colour-pair registry (pairs 1-19 reserved for map tiles in client.py)
_pair_cache: dict = {}
_next_pair: int   = 20


def _rgb_to_256(r: int, g: int, b: int) -> int:
    """Map an RGB triple to the nearest xterm-256 colour cube index (16–231)."""
    return 16 + 36 * round(r / 255 * 5) + 6 * round(g / 255 * 5) + round(b / 255 * 5)


def _pair_for(fg: tuple, bg: tuple) -> int:
    """Return (creating if needed) a curses colour pair for an (fg, bg) RGB pair."""
    global _next_pair
    key = (fg, bg)
    if key not in _pair_cache:
        curses.init_pair(_next_pair, _rgb_to_256(*fg), _rgb_to_256(*bg))
        _pair_cache[key] = _next_pair
        _next_pair += 1
    return _pair_cache[key]


def make_grid(hair: tuple, skin: tuple, clothes: tuple) -> list:
    """Return the 8×8 pixel grid for a character sprite."""
    H, S, C = hair, skin, clothes
    E = tuple(max(0, c - 70) for c in skin)          # eyes: darkened skin
    B = (38, 28, 18)                                  # boots: dark brown
    T = tuple(min(255, c + 90) for c in clothes)      # tie/detail: lighter accent
    X = EMPTY

    return [
        [X, H, H, H, H, H, X, X],   # hair top
        [H, S, S, S, S, X, X, X],   # forehead
        [H, S, E, S, E, X, X, X],   # eyes
        [X, S, S, S, S, X, X, X],   # nose / mouth
        [C, C, C, T, C, X, X, X],   # shoulders
        [C, C, C, T, C, C, S, X],   # chest
        [S, C, C, C, C, X, X, X],   # legs
        [X, B, B, X, B, B, X, X],   # feet
    ]


def flip_grid(grid: list) -> list:
    """Mirror a pixel grid horizontally."""
    return [row[::-1] for row in grid]


def draw_sprite(win, y: int, x: int,
                hair: tuple, skin: tuple, clothes: tuple,
                facing: str = "right") -> None:
    """
    Draw the 8×8 sprite at screen cell (y, x).
    Occupies 8 columns × 4 terminal rows.
    """
    if curses.COLORS < 256:
        try:
            win.addstr(y + 1, x + 3, "@", curses.A_BOLD)
        except curses.error:
            pass
        return

    grid = make_grid(hair, skin, clothes)
    if facing == "left":
        grid = flip_grid(grid)

    for i in range(0, len(grid), 2):
        top_row = grid[i]
        bot_row = grid[i + 1] if i + 1 < len(grid) else [EMPTY] * len(top_row)
        sy = y + i // 2
        for col_i, (top, bot) in enumerate(zip(top_row, bot_row)):
            tc = DARK if top is None else top
            bc = DARK if bot  is None else bot
            try:
                win.addch(sy, x + col_i, '▀', curses.color_pair(_pair_for(tc, bc)))
            except curses.error:
                pass
