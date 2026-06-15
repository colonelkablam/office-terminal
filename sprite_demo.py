#!/usr/bin/env python3
"""
office-terminal sprite demo v2
Define sprite as a pixel grid (RGB tuples), render with ▀ half-blocks.
Each terminal row = 2 pixel rows  →  8 pixel rows display in 4 terminal rows.
"""

import os
import shutil

RESET = "\033[0m"

def fg(r, g, b): return f"\033[38;2;{r};{g};{b}m"
def bg(r, g, b): return f"\033[48;2;{r};{g};{b}m"

DARK = (12, 12, 18)   # terminal background
_ = None              # transparent pixel

def render_grid(grid):
    """Render a pixel grid using ▀ half-blocks (2 pixel rows per terminal row)."""
    lines = []
    for y in range(0, len(grid), 2):
        top_row = grid[y]
        bot_row = grid[y + 1] if y + 1 < len(grid) else [None] * len(top_row)
        line = ""
        for top, bot in zip(top_row, bot_row):
            tc = top if top is not None else DARK
            bc = bot if bot is not None else DARK
            line += f"{fg(*tc)}{bg(*bc)}▀"
        line += RESET
        lines.append(line)
    return lines

def flip_grid(grid):
    """Mirror a pixel grid horizontally (face left ↔ face right)."""
    return [row[::-1] for row in grid]


def make_grid(hair, skin, clothes):
    H, S, C = hair, skin, clothes
    E = tuple(max(0, c - 70) for c in skin)        # eyes: darkened skin tone
    B = (38, 28, 18)                                # boots: dark brown
    T = tuple(min(255, c + 90) for c in clothes)   # tie/detail: lighter accent

    return [
        [_, H, H, H, H, H, _, _],   # hair full
        [H, S, S, S, S, _, _, _],   # forehead
        [H, S, E, S, E, _, _, _],   # eyes
        [_, S, S, S, S, _, _, _],   # nose
        [C, C, C, T, C, _, _, _],   # shoulders
        [C, C, C, T, C, C, S, _],   # chest
        [S, C, C, C, C, _, _, _],   # legs
        [_, B, B, _, B, B, _, _],   # feet
    ]

def make_sprite(hair, skin, clothes, facing="right"):
    grid = make_grid(hair, skin, clothes)
    if facing == "left":
        grid = flip_grid(grid)
    return render_grid(grid)


# ── Class colours ─────────────────────────────────────────────────────────────
PM_SUIT    = (28,  72, 165)   # corporate navy
DEV_HOOD   = (60,  30, 130)   # dark hoodie purple
CLERK_WEAR = (140, 120, 80)   # beige office wear

# (name, hair, skin, clothes)
characters = [
    ("PM / Warrior",   (80,  48,  12),  (238, 195, 145), PM_SUIT),
    ("Dev / Mage",     (22,  22,  22),  (200, 158, 118), DEV_HOOD),
    ("Clerk / Cleric", (185, 148, 60),  (252, 218, 178), CLERK_WEAR),
]

# ── Render facing right ────────────────────────────────────────────────────────
print("\n  Facing right →")
sprites_r = [(name, make_sprite(h, s, c, "right")) for name, h, s, c in characters]
for row_i in range(len(sprites_r[0][1])):
    print("    ".join(sp[row_i] for _, sp in sprites_r))
print()
for name, _sp in sprites_r:
    print(f"{name:<22}", end="  ")

# ── Render facing left ─────────────────────────────────────────────────────────
print("\n\n  ← Facing left")
sprites_l = [(name, make_sprite(h, s, c, "left")) for name, h, s, c in characters]
for row_i in range(len(sprites_l[0][1])):
    print("    ".join(sp[row_i] for _, sp in sprites_l))
print()
for name, _sp in sprites_l:
    print(f"{name:<22}", end="  ")

# ── Terminal size info ─────────────────────────────────────────────────────────
cols, rows = shutil.get_terminal_size(fallback=(80, 24))
colorterm = os.environ.get("COLORTERM", "not set")
term = os.environ.get("TERM", "not set")
truecolor = colorterm in ("truecolor", "24bit")
print(f"\n\n  Your terminal: {cols}×{rows}")
print(f"  TERM={term}  COLORTERM={colorterm}  24-bit color: {'YES ✓' if truecolor else 'NO — set COLORTERM=truecolor in your shell profile'}")
print(f"  Recommended minimum: 120×40  (you are {'✓ good' if cols >= 120 and rows >= 40 else '✗ too small'})")
print(f"  Comfortable:         160×50  (you are {'✓ good' if cols >= 160 and rows >= 50 else '✗ too small'})")
print()
print("  Suggested layout at 120×40:")
print("  ┌─────────────[MAP 90×34]──────────────┬──[STATS 28×34]──┐")
print("  │                                       │  HP / MP / XP   │")
print("  │   Dungeon viewport (server-enforced)  │  Inventory      │")
print("  │   same dimensions for all clients     │  Equipment      │")
print("  ├───────────────────────────────────────┴─────────────────┤")
print("  │  Message log / combat feed                    [120×4]   │")
print("  └──────────────────────────────────────────────────────────┘")
print()
