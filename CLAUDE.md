# CLAUDE.md

Guidance for Claude Code when working in this repository.

## Project

**office-terminal** — a terminal-based roguelike dungeon crawler with an office theme.
Real-time tick-based multiplayer over local network using Python asyncio (server) + curses (client).

### Classes / roles
| In-game label     | Role    | Class key  |
|-------------------|---------|------------|
| Project Manager   | Warrior | `warrior`  |
| Developer         | Mage    | `mage`     |
| Office Clerk      | Cleric  | `cleric`   |

## Running the game

```bash
./run.sh              # start server + local client (solo / host)
./run.sh <server-ip>  # join a remote game (client only)
```

Or separately:

```bash
python3 server.py
python3 client.py [host]   # default host = 127.0.0.1
```

Demo the sprite renderer standalone:

```bash
python3 sprite_demo.py
```

## Terminal requirements

- Size: **132 × 43** (set in `game/config.py`)
- 256-color support required for sprites; falls back to `@` in 8-color terminals
- Add `export COLORTERM=truecolor` to `~/.bashrc` to enable full 24-bit palette

## Layout (132 × 43)

```
row 0          header bar (reversed)
rows 1–38      map viewport (cols 0–99) │ side panel (cols 101–131)
               col 100 = │ border
row 39         horizontal separator
rows 40–42     message log (3 lines)
```

## Sprites

8 × 8 pixel sprites rendered with Unicode half-blocks (`▀`, U+2580).
- 1 terminal row = 2 pixel rows → 8px tall sprite = **4 terminal rows × 8 cols**
- Each `▀` cell: foreground = top pixel colour, background = bottom pixel colour
- Colours mapped to xterm-256 cube: `16 + 36*round(r/255*5) + 6*round(g/255*5) + round(b/255*5)`
- curses colour pairs 1–19 reserved for map tiles; sprite pairs allocated from 20 upward via `_pair_cache` in `game/sprite.py`
- `EMPTY = None` is the transparent sentinel in `game/sprite.py` — **never use `_` for this** (name clash with loop throwaway variables)

## File structure

```
office-terminal/
├── CLAUDE.md          — this file
├── .gitignore
├── run.sh             — convenience launcher
├── server.py          — asyncio TCP server, game loop at TICK_RATE=15 tps
├── client.py          — curses client, ~25 fps render loop
├── sprite_demo.py     — standalone sprite renderer (proof of concept)
└── game/
    ├── __init__.py
    ├── config.py      — constants (TERM_W/H, MAP_W/H, HOST, PORT, class colours)
    ├── dungeon.py     — BSP dungeon generation → (tiles, rooms, spawn)
    ├── entities.py    — Player class with move(), to_dict()
    ├── world.py       — World (dungeon + players), viewport slicing, state_for()
    └── sprite.py      — draw_sprite(), make_grid(), flip_grid()
```

## Network protocol

- Newline-delimited JSON over TCP
- Client → server: `{"type": "input", "key": "w"}` etc.
- Server → client: JSON snapshot each tick via `world.state_for(pid)`:
  ```json
  {"tick": 42, "view": [...], "view_x": 0, "view_y": 0, "players": [...], "messages": [...]}
  ```

## Key design decisions

- Server owns all game state; clients only send input and render received state
- Viewport scrolling: server computes a tile-slice centred on each player
- Player sprites drawn on the map *after* tiles (overlay), *before* border/panel (so bleed is overwritten)
- Sprite centred on tile: `draw_sprite(win, sy-2, sx-4, ...)` (−2 rows, −4 cols)
